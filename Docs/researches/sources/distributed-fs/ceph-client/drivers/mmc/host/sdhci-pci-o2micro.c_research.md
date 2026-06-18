# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-o2micro.c

## Purpose
This file implements BayHub/O2Micro PCI SDHCI fixups exported as `sdhci_o2`. It covers older broken-ADMA devices, SDS/Seabird/Fujin2 variants, and GG8 986x controllers with SD Express support. Its main work is PCI config register initialization, DLL/PLL recovery, custom tuning, clock programming, power cleanup, card-detect stabilization, and resume replay.

## Important APIs, Types, And Functions
`struct o2_host` stores `dll_adjust_count` in per-slot private memory. `sdhci_pci_o2_probe()` performs chip-level PCI config initialization, while `sdhci_pci_o2_probe_slot()` adjusts per-host MMC capabilities and callbacks. `sdhci_o2_execute_tuning()` handles HS200/SDR104/SDR50 tuning and falls back to `sdhci_execute_tuning()` for other modes. `sdhci_o2_dll_recovery()` cycles base-clock DMDN values from `dmdn_table` to recover DLL lock. Clock and power are handled by `sdhci_pci_o2_set_clock()`, `sdhci_o2_enable_clk()`, and `sdhci_pci_o2_set_power()`. SD Express setup for GG8 is in `sdhci_pci_o2_init_sd_express()`.

## Control Flow
Chip probe switches on PCI device ID. Older 8220/8221/8320/8321 devices unlock write-protected config space, disable ADMA, force SDMA capabilities, and disable infinite transfer mode. SDS/Fujin2/Seabird variants unlock write protection, program PLL/tuning/clock request/debounce registers, optionally enable LEDs, and run Fujin2-specific performance, L1, UHS-II, and capability setup. GG8 986x devices configure software mode switching, VDD source, drive strength, and output delay.

Slot probe initializes `dll_adjust_count`, derives 8-bit support from SDHCI capabilities, marks DDR50/preset quirks, enables MSI, installs O2 tuning, and adds device-specific capabilities. Seabird may force 1.8 V eMMC-only mode and custom card-detect. GG8 advertises SD Express/1.2 V and installs `init_sd_express`.

During tuning, the driver forces L0, adjusts output phase for selected devices, waits for DLL lock, performs DLL recovery if lock detection fails, temporarily downgrades 8-bit bus width to 4-bit because hardware tuning does not support 8-bit eMMC, runs hardware tuning, restores bus width, clears L0 force, resets command/data, and clears HS400 tuning state.

## State And Persistence
The only driver-private persistent value is `o2_host->dll_adjust_count`; it prevents retrying the same DMDN entries forever. Hardware state includes write-protected PCI config registers, PLL base-clock values, output clock source/phase, SD Express switch bits, LED enable state, capability registers, and DLL watchdog settings. Resume calls `sdhci_pci_o2_probe()` again before generic host resume to replay config-space setup.

## Dependencies And Integration Points
The code depends on `sdhci-pci.h` IDs and fixup hooks, PCI config access, SDHCI register access, MMC tuning helpers, and `read_poll_timeout()`/`readx_poll_timeout()` for lock detection. Integration is through `.probe`, `.probe_slot`, `.resume`, `.ops`, and `.priv_size` in `sdhci_o2`.

## Risks
Many paths unlock and relock O2 write-protected config space; failures can leave hardware partially programmed. DLL recovery intentionally manipulates clocks while probing card detect, which can affect removable cards. Tuning changes bus width temporarily, so ordering with MMC core state matters. SD Express fallback changes `mmc->ios.timing` to legacy and powers off VDD2, which must match core expectations. Fixed magic values make regression tests hardware-dependent.

## Test Signals
Exercise each device family, especially Fujin2, Seabird, and GG8. Look for successful MSI or fallback, stable CD debounce, DLL lock/recovery logs, HS200/SDR104 tuning, 8-bit eMMC recovery after tuning, SD Express success/fallback, and correct behavior after suspend/resume where PCI config is replayed.

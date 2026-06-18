# Research: subset-b-004277

This grouped report covers SDHCI PCI fixups and platform glue under `sources/distributed-fs/ceph-client/drivers/mmc/host/`. Each section is bounded for deterministic reconciliation into the required per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-dwc-mshc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-dwc-mshc.c

## Purpose
This file provides the Synopsys DWC_MSHC PCI-specific SDHCI fixup exported as `sdhci_snps`. It replaces the generic clock callback with a Synopsys MMCM-aware implementation while otherwise delegating DMA, bus-width, reset, and UHS signaling to the common SDHCI/PCI helpers.

## Important APIs, Types, And Functions
The key entry point is `sdhci_snps_set_clock()`, installed through `sdhci_snps_ops.set_clock`. The exported `const struct sdhci_pci_fixes sdhci_snps` is consumed by the generic `sdhci-pci` device table through `sdhci-pci.h`. Vendor registers are found by reading `SDHCI_VENDOR_PTR_R`, then adding that vendor pointer to `SDHC_GPIO_OUT` and `SDHC_AT_CTRL_R`. High-speed clock programming uses fixed MMCM DRP constants for 100 MHz and 200 MHz.

## Control Flow
Clock changes first disable Synopsys software-managed RX tuning by clearing `SDHC_SW_TUNE_EN`. Requests at or below 52 MHz fall through to `sdhci_set_clock()`. Faster requests assert the MMCM reset bit, write either the 100 MHz or 200 MHz divider/feedback settings, deassert reset, then directly enable programmable clock mode, internal clock, and card clock in `SDHCI_CLOCK_CONTROL`.

## State And Persistence
The file keeps no private host state. Persistent effects are hardware register state: MMCM divider/feedback programming, vendor AT control state, and the card/internal clock bits. The routine does not update a private cache beyond the common SDHCI state maintained by core helpers.

## Dependencies And Integration Points
It depends on `sdhci.h` for host register access and `sdhci-pci.h` for the `sdhci_pci_fixes` contract and `sdhci_pci_enable_dma()`. Integration happens when the PCI glue selects `sdhci_snps` for `PCI_DEVICE_ID_SYNOPSYS_DWC_MSHC`.

## Risks
The implementation assumes only 100 MHz and 200 MHz require explicit MMCM programming; any other rate above 52 MHz is coerced to the 200 MHz settings. The code writes MMCM registers without polling for lock, so clock instability would surface later as command/data failures. Register offsets are hard-coded and depend on the vendor pointer being valid.

## Test Signals
Useful signals are successful enumeration at legacy and high-speed rates, no tuning regressions after clearing software tuning, stable transfers at 100/200 MHz, and absence of command/data timeout logs after repeated clock switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-dwc-mshc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-gli.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-gli.c

## Purpose
This file contains Genesys Logic PCI SDHCI fixups for GL9750, GL9755, GL9763E, and GL9767 controllers. It layers vendor register programming, custom clocks, tuning, MSI setup, UHS-II/SD Express handling, CQHCI support for GL9763E eMMC, and power-management quirks onto the generic `sdhci-pci` framework.

## Important APIs, Types, And Functions
The exported fixup objects are `sdhci_gl9750`, `sdhci_gl9755`, `sdhci_gl9763e`, and `sdhci_gl9767`. Each supplies a `struct sdhci_ops` table and probe callbacks such as `gli_probe_slot_gl9750()`, `gli_probe_slot_gl9755()`, `gli_probe_slot_gl9763e()`, and `gli_probe_slot_gl9767()`. GL9750/9755 clock paths use `gl975*_set_ssc_pll_*()` and custom `set_clock` functions to program spread-spectrum PLL settings. GL9750 also has `gl9750_execute_tuning()` with a two-pass RX-invert tuning fallback. GL9767 adds UHS-II and SD Express support through `sdhci_pci_uhs2_add_host()`, `sdhci_gl9767_set_power()`, `sdhci_gl9767_reset()`, `gl9767_init_sd_express()`, and vendor PHY programming. GL9763E integrates command queueing through `gl9763e_add_host()`, `sdhci_gl9763e_cqhci_irq()`, and `sdhci_gl9763e_cqhci_ops`.

## Control Flow
Slot probe performs one-time vendor setup, enables MSI if possible, adjusts advertised MMC capabilities, and enables SDHCI v4 mode. GL9750/9755 probes disable SDIO, set ASPM/L1 delay values, mask PCIe AER replay timer timeout, and program vendor tuning/PLL defaults. GL9767 additionally marks SD Express support, installs `init_sd_express`, configures debounce and UHS-II PHY registers, and uses UHS-II-aware add/remove host callbacks. GL9763E configures eMMC-only capabilities, enables HS200/HS400/HS400ES and optional CQE/DCMD based on mailbox bits, then uses a custom add-host path: setup SDHCI, allocate/init CQHCI, add the host, and disable low-power negotiation.

During runtime operations, clock callbacks disable PLL/SSC, calculate SDHCI divisors, program vendor PLLs for selected high rates, then re-enable the SDHCI clock. Reset callbacks ensure an internal clock exists, handle UHS-II SD-trans reset when needed, and reapply vendor defaults. Voltage-switch callbacks add controller-specific delays. Power callbacks mask overcurrent interrupts around power toggles and manage VDD2/UHS-II bits.

## State And Persistence
Most state is held in hardware registers and PCI config space. The driver mutates `host->pwr`, `host->clock`, `host->mmc->caps/caps2`, `host->mmc_host_ops`, `host->irq`, and CQHCI private state. GL9763E PM paths persist low-power negotiation policy across runtime/system suspend and resume. PLL, SSC, ASPM delay, debounce, UHS-II PHY, and SD Express mode bits persist until reset or reprogramming, so resume callbacks replay MSI and host state.

## Dependencies And Integration Points
The file depends on PCI config access, Open Firmware properties for Apple ARM64 CD/WP inversion, SDHCI core helpers, `sdhci-pci` fixup plumbing, UHS-II helpers from `sdhci-uhs2.h`, CQHCI support, and MMC timing/capability definitions. It integrates through PCI IDs declared in `sdhci-pci.h` and selected by the generic PCI driver.

## Risks
The code has many timing-sensitive register sequences with fixed millisecond and microsecond waits. PLL programming, VHS read/write windows, UHS-II reset ordering, and overcurrent masking can regress card detection or power cycling if reordered. GL9750 tuning deliberately returns success while storing errors in `host->tuning_err`, so callers must respect SDHCI tuning semantics. GL9763E CQHCI setup crosses SDHCI and CQHCI ownership, making suspend/resume and IRQ routing high-risk. Apple-specific OF inversion settings affect removable media detection and write protect.

## Test Signals
Test with each supported PCI ID. Signals include successful MSI allocation or clean INTx fallback, stable enumeration after suspend/resume, GL9763E CQE traffic and DCMD operation, GL9767 UHS-II and SD Express mode transitions, SDR104 tuning success/fallback, no replay timer AER noise, correct CD/WP polarity on OF systems, and no overcurrent interrupt storm during power changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-gli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-o2micro.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-o2micro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci.h

## Purpose
This header defines the private contract between the generic SDHCI PCI driver and vendor-specific PCI fixup files. It centralizes PCI device IDs, table-construction macros, slot/chip data structures, fixup callbacks, and exported fixup declarations for Arasan, Synopsys, O2Micro, and Genesys devices.

## Important APIs, Types, And Functions
`struct sdhci_pci_fixes` is the central extension point. It carries SDHCI `quirks`, `quirks2`, runtime-PM policy, optional chip and slot probe callbacks, host add/remove callbacks, slot remove hooks, sleep/runtime PM callbacks, a replacement `sdhci_ops` table, optional CD GPIO override DMI table, and per-slot private size. `struct sdhci_pci_slot` binds a `struct sdhci_host` to its owning `struct sdhci_pci_chip`, card-detect override data, optional hardware reset callback, and aligned private storage. `struct sdhci_pci_chip` tracks the PCI device, aggregate quirks, PM flags, selected fixups, slot count, and slot pointers. `sdhci_pci_priv()` returns the vendor-private tail memory. Declarations expose `sdhci_pci_uhs2_add_host()`, `sdhci_pci_uhs2_remove_host()`, `sdhci_pci_resume_host()`, and `sdhci_pci_enable_dma()`.

## Control Flow
The generic PCI driver matches devices using `SDHCI_PCI_DEVICE`, `SDHCI_PCI_SUBDEVICE`, or `SDHCI_PCI_DEVICE_CLASS`. Those macros store a pointer to a `sdhci_<cfg>` fixup object in `driver_data`. During probe, the core allocates a chip and slots, applies chip-level callbacks, attaches per-slot private memory sized by `priv_size`, applies slot callbacks, and invokes custom add/remove/PM hooks when provided.

## State And Persistence
The structures in this header define all persistent PCI SDHCI driver state across probe, runtime, and PM transitions. Vendor files mutate chip and slot fields indirectly through these structures, and the generic PCI driver uses them to replay resume, remove dead hosts, and track runtime retuning flags.

## Dependencies And Integration Points
It depends on PCI class/vendor/device constants, `struct sdhci_host`, `struct sdhci_ops`, DMI declarations, and optional PM config. Every `sdhci-pci-*` vendor file includes this header, and the central `sdhci-pci.c` implementation consumes the declarations and structures.

## Risks
The callback structure is broad and hardware-specific; misconfigured fixup tables can route a device to the wrong ops or omit required private storage. `private[]` alignment means callers must use `sdhci_pci_priv()` rather than assuming fixed layout. PM callback availability changes with kernel config, so code must remain correct with and without `CONFIG_PM`/`CONFIG_PM_SLEEP`.

## Test Signals
Build coverage should include PCI vendor fixup files with different PM configs. Runtime signals are correct device-table binding, expected quirk propagation, per-slot private state availability, UHS-II add/remove paths for relevant devices, and DMA enable behavior through `sdhci_pci_enable_dma()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pic32.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pic32.c

## Purpose
This file is the Microchip PIC32 platform SDHCI driver. It wraps `sdhci-pltfm` allocation with PIC32-specific clocks, bus-width handling, shared-bus selection, write-protect behavior, platform DMA setup, and OF matching for `microchip,pic32mzda-sdhci`.

## Important APIs, Types, And Functions
`struct pic32_sdhci_priv` stores the platform device and two clocks: `sys_clk` and `base_clk`. `pic32_sdhci_get_max_clock()` reports `base_clk` rate. `pic32_sdhci_set_bus_width()` updates SDHCI host-control width bits and always applies the PIC32 card-detect errata settings `SDHCI_CTRL_CDSSEL` and not `SDHCI_CTRL_CDTLVL`. `pic32_sdhci_get_ro()` always returns writable because hardware write-protect is unstable. `pic32_sdhci_probe()`, `pic32_sdhci_remove()`, and `pic32_sdhci_driver` implement the platform lifecycle.

## Control Flow
Probe calls `sdhci_pltfm_init()` with `sdhci_pic32_pdata`, obtains the `sdhci_pltfm_host` and private PIC32 data, optionally calls board `setup_dma()` with ADMA FIFO thresholds, gets/enables `sys_clk`, gets/enables `base_clk`, parses OF MMC properties, checks slot type from capabilities, configures shared-bus clock/IRQ pin selection if needed, then registers the host with `sdhci_add_host()`. Remove checks whether the controller appears dead by reading all-ones interrupt status, removes the host, and disables both clocks.

## State And Persistence
Persistent software state is limited to the two prepared clocks in private data. Hardware state includes shared-bus pin-selection bits and host-control card-detect select/test bits. Quirks are fixed through `sdhci_pic32_pdata`: no HISPD bit and no 1.8 V signaling.

## Dependencies And Integration Points
The driver depends on `sdhci-pltfm`, common SDHCI helpers, Microchip platform data for optional DMA setup, two named clocks, and MMC OF parsing. Integration is through the platform driver and OF compatible table.

## Risks
The error path disables `base_clk` in `err_base_clk` even when failures can occur before it is enabled, so clock pointer validity depends on branch ordering. The private pointer in remove is cast with `sdhci_priv(host)` even though probe accessed PIC32 data through `sdhci_pltfm_priv()`, which is a pattern worth reviewing because `sdhci_priv()` returns the platform wrapper, not the private tail. Hardware write-protect is intentionally ignored, so media WP tests cannot rely on this driver.

## Test Signals
Probe should show successful host registration, correct `base_clk` max frequency, shared-bus slot operation, stable card detect despite errata bits, DMA setup callback execution on platform-data systems, and clean clock disable on removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pic32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pltfm.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pltfm.c

## Purpose
This file is the reusable platform/OF helper layer for SDHCI host drivers. It allocates and initializes `struct sdhci_host` for memory-mapped platform devices, applies common properties and compatibility quirks, registers/removes hosts, and provides shared system-sleep PM operations.

## Important APIs, Types, And Functions
Exported APIs include `sdhci_pltfm_clk_get_max_clock()`, `sdhci_get_property()`, `sdhci_pltfm_init()`, `sdhci_pltfm_init_and_add_host()`, `sdhci_pltfm_remove()`, `sdhci_pltfm_suspend()`, `sdhci_pltfm_resume()`, and `sdhci_pltfm_pmops`. Static helpers include `sdhci_wp_inverted()` and `sdhci_get_compatibility()`. The default ops table uses generic clock, bus-width, reset, and UHS signaling callbacks.

## Control Flow
`sdhci_pltfm_init()` maps MMIO resource 0, obtains IRQ 0, allocates an SDHCI host with room for `struct sdhci_pltfm_host` plus caller private data, assigns IO address, IRQ, hardware name, ops, and quirks, and stores the host in platform drvdata. `sdhci_get_property()` reads generic properties: auto CMD12, 1-bit-only/bus-width, inverted write protect, broken card detect, no 1.8 V, Freescale compatibility quirks, and optional clock-frequency into `pltfm_host->clock`. `sdhci_pltfm_init_and_add_host()` combines init, property parsing, and `sdhci_add_host()`.

## State And Persistence
The helper initializes persistent platform state in `struct sdhci_pltfm_host`, especially `clk`, `clock`, and `xfer_mode_shadow` for BE byte-swapper users. It persists device properties as SDHCI quirks and quirks2. PM suspend marks retune needed unless tuning mode 3, suspends the host, and disables `pltfm_host->clk`; resume reenables the clock and resumes the host.

## Dependencies And Integration Points
It is used by many platform drivers in the same directory. It depends on Linux device properties, platform resource APIs, optional PowerPC machine checks for legacy WP inversion, clock framework, and SDHCI core APIs.

## Risks
Callers must initialize `pltfm_host->clk` before using shared PM ops, otherwise suspend/resume will operate on a null or invalid clock. Property parsing mutates quirks before host setup, so duplicate or conflicting board-specific parsing can change behavior. Legacy Freescale compatibility quirks are applied by string matching and can affect timeout/DMA behavior globally for those compatibles.

## Test Signals
Coverage should include successful platform probe through `sdhci_pltfm_init_and_add_host()`, property-to-quirk mapping, dead-host removal when interrupt status is all ones, suspend/resume retune marking, and clock disable/enable ordering with drivers that use `sdhci_pltfm_pmops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pltfm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pltfm.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pltfm.h

## Purpose
This header defines the shared data structures and helper declarations for SDHCI platform drivers. It also provides optional big-endian 32-bit byte-swapper accessors used by platforms whose register windows require swapped sub-word addressing.

## Important APIs, Types, And Functions
`struct sdhci_pltfm_data` carries a platform driver's ops and initial quirk sets. `struct sdhci_pltfm_host` stores the platform clock, optional fixed clock frequency, transfer-mode shadow, and aligned private storage. `sdhci_pltfm_priv()` returns the private tail after the wrapper. Declarations expose `sdhci_get_property()`, `sdhci_get_of_property()`, `sdhci_pltfm_init()`, `sdhci_pltfm_init_and_add_host()`, `sdhci_pltfm_remove()`, `sdhci_pltfm_clk_get_max_clock()`, `sdhci_pltfm_pmops`, and sleep PM helpers.

## Control Flow
Platform drivers pass `struct sdhci_pltfm_data` and a private-size value into `sdhci_pltfm_init()`. The returned host's `sdhci_priv(host)` points to `struct sdhci_pltfm_host`; driver-private data is retrieved through `sdhci_pltfm_priv()`. With the BE byte-swapper config enabled, drivers can install accessors that map SDHCI sub-word operations onto big-endian 32-bit MMIO. The writew accessor shadows `SDHCI_TRANSFER_MODE` and emits transfer mode together with `SDHCI_COMMAND`.

## State And Persistence
The header defines persistent per-host platform state rather than storing it itself. `xfer_mode_shadow` is important for byte-swapped controllers because transfer mode must be combined with command writes. Conditional PM stubs return success when sleep PM is disabled, allowing drivers to reference helpers without config-specific code.

## Dependencies And Integration Points
It includes the clock framework, platform devices, and `sdhci.h`. Nearly all platform SDHCI glue drivers include it to use the common allocation, private-data layout, and optional PM operations.

## Risks
The private-data layout is easy to misuse: `sdhci_priv(host)` is the platform wrapper, while `sdhci_pltfm_priv()` is driver-private data. The BE byte-swapper accessors rely on exact SDHCI command/transfer register semantics and can corrupt command issue order if reused incorrectly. Conditional accessor definitions mean build coverage must include both endian configurations if touched.

## Test Signals
Compile platform drivers with and without `CONFIG_PM_SLEEP` and with BE byte-swapper enabled where possible. Runtime signals are correct private pointer use, command issuance on byte-swapped controllers, and shared PM helper linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pltfm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pxav2.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pxav2.c

## Purpose
This file supports Marvell PXA v1/v2 SDHCI-compatible platform controllers. It adds PXA-specific reset configuration, clock-gating and delay setup, 8-bit bus-width programming, legacy PXA168 SDIO erratum handling using a dummy CMD0 and pinctrl, platform/OF data parsing, and shared `sdhci-pltfm` PM integration.

## Important APIs, Types, And Functions
`struct sdhci_pxav2_host` stores a deferred SDIO request and optional pinctrl states. `pxav2_reset()` replays clock delay and clock-gating settings after full reset. `pxav1_readw()` works around SDH2/SDH4 host-version access on PXA168. `pxav1_irq()` and `pxav1_request_done()` implement the SDIO workaround. `pxav2_mmc_set_bus_width()` writes both SDHCI host-control bits and PXA `SD_CE_ATA_2` MMC width/card bits. Variant data selects `pxav1_sdhci_ops` or `pxav2_sdhci_ops`.

## Control Flow
Probe allocates through `sdhci_pltfm_init()`, enables IO and optional core clocks, installs baseline quirks for broken ADMA, broken timeout, and broken clock-base capabilities, selects variant from OF match data, parses platform or OF data for non-removable, 8-bit, delay, host caps, and PM caps, configures optional pinctrl states for the PXA168 SDIO workaround, then calls `sdhci_add_host()`.

For PXA v1 SDIO requests, completion is intercepted. If an SDIO direct or extended command succeeded, the driver resets the data port, records the original request, optionally switches CMD pin to GPIO-high, issues a dummy CMD0 to restart the clock, and delays `mmc_request_done()` until `pxav1_irq()` observes the dummy command completion. IRQ then clears command status, restores pinctrl default, clears `sdio_mrq`, and completes the original request.

## State And Persistence
Persistent state includes the optional pending `sdio_mrq`, pinctrl handles, clocks in `sdhci_pltfm_host`, platform flags/caps applied to `host->mmc`, and hardware clock-gating/delay registers replayed after full reset. The driver does not define custom suspend/resume beyond `sdhci_pltfm_pmops`.

## Dependencies And Integration Points
It depends on `sdhci-pltfm`, Marvell PXA platform data, OF properties such as `non-removable`, `bus-width`, and `mrvl,clk-delay-cycles`, optional pinctrl states `state_cmd_gpio` and `default`, and MMC SDIO command definitions.

## Risks
The SDIO erratum path is stateful and can deadlock request completion if the dummy CMD0 interrupt is lost or pinctrl states are missing on affected hardware. Reset-time delay/clock-gating programming depends on platform data and may not run for OF-created data unless populated correctly. Broken ADMA/timeout quirks reduce performance but avoid known failures.

## Test Signals
Test PXA v1 and v2 compatibles, SDIO direct/extended commands, dummy CMD0 completion, pinctrl transitions, 8-bit MMC bus-width programming, clock-delay OF properties, and suspend/resume through shared platform PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pxav2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pxav3.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pxav3.c

## Purpose
This file supports Marvell PXA v3 and Armada 38x SDHCI platform controllers. It extends `sdhci-pltfm` with MBUS window setup, Armada-specific capability corrections, UHS signaling clock feedback workarounds, pinctrl switching for high-speed modes, regulator-aware power control, runtime PM, and 74-clock initialization generation.

## Important APIs, Types, And Functions
`struct sdhci_pxa` stores core/IO clocks, prior power mode, optional Armada SDIO3 config MMIO, and pinctrl states. `mv_conf_mbus_windows()` programs MBUS DRAM windows from `mv_mbus_dram_info()`. `armada_38x_quirks()` reads capabilities early, maps optional `conf-sdio3`, and adjusts 1.8/3.3 V and SDR/DDR support for Armada errata. `pxav3_reset()`, `pxav3_gen_init_74_clocks()`, `pxav3_set_uhs_signaling()`, `pxav3_set_power()`, and `pxav3_set_clock()` implement the custom SDHCI ops.

## Control Flow
Probe initializes a host with `sdhci_pxav3_pdata`, enables IO and optional core clocks, sets MMC busy-response and 1.8 V DDR capabilities, applies Armada 38x quirks and MBUS windows when compatible, parses OF or platform data, applies caps/quirks, obtains optional pinctrl states, enables runtime PM with autosuspend, adds the host, enables wakeup for SDIO IRQ if requested, and drops the runtime PM reference.

Clock changes choose default pins below 100 MHz and UHS pins at higher rates, then call generic `sdhci_set_clock()`. UHS signaling updates host-control2 mode bits and, when `conf-sdio3` exists, applies Armada FE-2946959 feedback-clock/inversion settings for SDR50/DDR50 versus other modes. Power changes use `sdhci_set_power_noreg()` and then update `vmmc` regulator OCR. The 74-clock hook generates initial clocks when moving from power-up to power-on and warns if the hardware interrupt bit does not clear.

## State And Persistence
Persistent state includes prepared clocks, current `power_mode`, optional mapped SDIO3 config register, pinctrl state pointers, runtime PM active/suspended state, and MBUS window registers. Platform data derived from OF is stored in `pdev->dev.platform_data` for reset-time delay replay.

## Dependencies And Integration Points
The driver depends on `sdhci-pltfm`, PXA platform data, OF matching for `mrvl,pxav3-mmc` and `marvell,armada-380-sdhci`, `linux/mbus.h`, pinctrl, regulators via MMC core, and runtime PM. It registers as `sdhci-pxav3`.

## Risks
Armada capability correction is tightly tied to DT resources; missing `conf-sdio3` disables SDR50/DDR50 to avoid errata. MBUS setup maps a second resource manually and must match SoC memory topology. Runtime suspend disables clocks and marks retune, so missed resume ordering can break high-speed modes. Pinctrl at the 100 MHz threshold can affect signal integrity.

## Test Signals
Use DT variants for PXA v3 and Armada 38x, verify MBUS windows, confirm UHS capability filtering with and without `conf-sdio3`, check pinctrl transitions around 100 MHz, regulator OCR changes, 74-clock generation, runtime autosuspend/resume, and SDIO wakeup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pxav3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-s3c.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-s3c.c

## Purpose
This file is Samsung S3C/Exynos SDHCI glue. It handles multi-source bus clock selection, Samsung-specific control register programming, platform/OF card-detect and bus-width data, quirks for known controller limitations, and runtime/system PM for `s3c-sdhci` and Exynos-compatible devices.

## Important APIs, Types, And Functions
`struct sdhci_s3c` stores the host, platform device, platform data, current clock source, external CD IRQ, IO clock, up to four bus clocks, cached rates, and a no-divider flag. `struct sdhci_s3c_drv_data` selects quirks, no-divider mode, and ops for variants. `sdhci_s3c_set_clock()` chooses the best fixed source and configures Samsung control registers; `sdhci_cmu_set_clock()` additionally asks the clock framework to set the selected source rate for CMU/no-divider variants. `sdhci_s3c_parse_dt()` derives bus width and card-detect type from OF.

## Control Flow
Probe requires platform data or OF, obtains IRQ, allocates a host with private `sdhci_s3c`, copies/parses platform data, gets and enables the `hsmmc` IO clock, discovers `mmc_busclk.0..3`, maps MMIO, optionally configures board GPIOs, installs default or variant ops, applies a long set of quirks, maps card-detect policy into broken-CD/non-removable caps, applies width/caps/PM caps, enables runtime PM, parses generic MMC OF properties, and registers the host. Under `CONFIG_PM`, it may disable the IO clock after probe for non-internal card detect.

Clock setting evaluates all available source clocks, selects the smallest delta from the requested rate, enables the new source, disables the previous source, writes base-clock selection and Samsung control registers, then invokes generic SDHCI clock programming. Exynos CMU mode uses `clk_round_rate()` for min/max and `clk_set_rate()` before enabling the card clock.

## State And Persistence
The driver persists `cur_clk`, cached `clk_rates`, card-detect type, bus-width/caps, and runtime PM state. Hardware state includes `CONTROL2`, `CONTROL3`, `CONTROL4`, selected base clock, drive strength, feedback-clock flags, and SDHCI clock control. Suspend/runtime suspend mark retune when needed and disable active bus/IO clocks; resume reenables them and calls SDHCI resume helpers.

## Dependencies And Integration Points
It depends on Samsung platform data, OF compatibles `samsung,s3c6410-sdhci` and `samsung,exynos4210-sdhci`, clock framework, PM runtime, SDHCI core, and MMC OF parsing. It registers both a platform ID table and OF table.

## Risks
The best-clock calculation assumes fixed divisors unless `no_divider` is set; wrong variant data can select bad rates. Error paths after `sdhci_alloc_host()` return without explicit host free in some early failures, relying on managed allocations only for later resources. Multiple quirks disable DMA or alter busy behavior, so performance-sensitive changes need hardware validation. Runtime PM clock gating depends on `cur_clk` being valid.

## Test Signals
Verify S3C6410 and Exynos clock rates, source switching, card-detect modes, bus widths up to 8-bit, runtime autosuspend/resume, system suspend/resume retuning, and absence of internal-clock-stable failures in CMU mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-s3c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-spear.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-spear.c

## Purpose
This is a compact SDHCI platform driver for ST SPEAr SoCs. It manually allocates an SDHCI host, maps one MMIO resource, enables a single clock at 50 MHz, optionally requests GPIO card detect, applies a broken-ADMA quirk, and delegates normal SDHCI operation to generic ops.

## Important APIs, Types, And Functions
`struct spear_sdhci` stores the controller clock. The static `sdhci_pltfm_ops` table uses generic `sdhci_set_clock`, `sdhci_set_bus_width`, `sdhci_reset`, and `sdhci_set_uhs_signaling`. Lifecycle functions are `sdhci_probe()`, `sdhci_remove()`, `sdhci_suspend()`, and `sdhci_resume()`. The OF compatible is `st,spear300-sdhci`.

## Control Flow
Probe allocates `struct sdhci_host` with private clock storage, maps registers, sets hardware name and ops, obtains IRQ, applies `SDHCI_QUIRK_BROKEN_ADMA`, gets/enables the clock, tries to set it to 50 MHz, optionally requests card-detect GPIO through `mmc_gpiod_request_cd()`, registers the host, and stores drvdata. If card-detect GPIO probe defers or host add fails, it disables the clock.

Remove reads interrupt status to detect a dead controller, removes the host, and disables the clock. System suspend marks retune when needed, suspends the host, and disables the clock; resume enables the clock and resumes the host.

## State And Persistence
Software state is just the prepared clock in private data plus host quirks/caps initialized at probe. Hardware state is the SDHCI register block and clock rate. No runtime PM or custom tuning state exists.

## Dependencies And Integration Points
The driver depends on platform resources, clock framework, optional MMC slot GPIO card-detect descriptors, common SDHCI core, and OF platform binding. It does not use `sdhci-pltfm` allocation despite resembling it.

## Risks
The driver name is generic (`sdhci`) and local ops symbol is named `sdhci_pltfm_ops`, which can be confusing during maintenance. It sets the clock to 50 MHz but only logs failure at debug level. Broken ADMA disables a performance path. The suspend path uses `clk_disable()` rather than `clk_disable_unprepare()`, matching probe's prepared state but requiring balanced enable counts.

## Test Signals
Expected signals are successful OF probe, 50 MHz clock setup or acceptable debug warning, optional CD GPIO handling including `-EPROBE_DEFER`, clean dead-host removal, and system sleep/resume with retune.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-spear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-sprd.c

## Purpose
This file supports Spreadtrum/Unisoc R11 SDHCI controllers. It implements non-standard register access rules, custom clock division and PHY DLL handling, PHY delay tuning from device tree, software queue integration, regulator/pinctrl voltage switching, HS400 enhanced strobe, SD high-speed command/data tuning, and runtime PM.

## Important APIs, Types, And Functions
`struct sdhci_sprd_host` stores version, three clocks, pinctrl states, base rate, a backup of host flags, and per-timing PHY delay values. `sdhci_sprd_ops` overrides read/write accessors, clock, power, min/max clock, UHS signaling, hardware reset, timeout count, read-only state, and request completion. Important helpers include `sdhci_sprd_calc_div()`, `_sdhci_sprd_set_clock()`, `sdhci_sprd_enable_phy_dll()`, `sdhci_sprd_set_uhs_signaling()`, `sdhci_sprd_voltage_switch()`, `sdhci_sprd_hs400_enhanced_strobe()`, `sdhci_sprd_tuning()`, and `sdhci_sprd_phy_param_parse()`.

## Control Flow
Probe allocates through `sdhci_pltfm_init()` with Spreadtrum quirks, sets a 64-bit DMA mask, overrides MMC host ops for request handling, HS400 ES, SD high-speed tuning, and voltage switch, parses MMC OF properties, sets atomic request handling for non-removable cards or deferred completion for removable cards, parses PHY delay properties, obtains optional pinctrl states, gets/enables `sdio`, `enable`, and optional `2x_enable` clocks, initializes DLL backup mode, enables runtime PM, enables SDHCI v4 mode, reads caps but clears UHS-I capability bits so DT controls exposure, gets regulators, performs `sdhci_setup_host()`, initializes `mmc_hsq`, adds the host, and arms autosuspend.

Clock programming computes the Spreadtrum divider, writes SDHCI clock control through `sdhci_enable_clk()`, toggles automatic inner/outer clock bits above 400 kHz, updates DLL inversion for low clock rates, and enables the PHY DLL above 52 MHz. UHS signaling writes non-standard HS200/HS400/HS400ES mode encodings and applies per-timing PHY delay. SD high-speed tuning sweeps 0..255 delay samples, records pass/fail, selects the middle of the longest passing range, and writes the resulting delay field.

## State And Persistence
Persistent state includes cached `base_rate`, `flags` backup used to restore auto CMD23 behavior per request, PHY delay table, pinctrl state, and runtime PM state. Hardware state includes DLL config/delay registers, debounce backup bits, busy-position auto-clock bits, non-standard software reset bit 3, and regulator state. Runtime suspend/resume gates clocks and `mmc_hsq`.

## Dependencies And Integration Points
The driver depends on `sdhci-pltfm`, `mmc_hsq`, pinctrl, regulators, OF properties `sprd,phy-delay-*`, runtime PM, and SDHCI v4 support. It registers for `sprd,sdhci-r11`.

## Risks
Register access is non-standard: max-current is synthetic, block-count writes are ignored, interrupt enables are masked, and reset bit 3 must be preserved except for explicit hardware reset. Generic SDHCI changes can break these assumptions. Tuning allocates a 256-byte result buffer and sends many status/switch commands, so failures can be timing/card dependent. Auto CMD23 is disabled per request when CMD23 stuff bits conflict with v4.10 ARGUMENT2 semantics.

## Test Signals
Validate removable and non-removable paths, HSQ request finalization, voltage switch pinctrl/regulator behavior, HS400 enhanced strobe delay, SD high-speed tuning range selection, DLL lock logs above 52 MHz, auto CMD23 disable for stuffed CMD23, runtime PM clock gating, and hardware reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-st.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-st.c

## Purpose
This file supports STMicroelectronics SoC SDHCI controllers, especially STiH407 FlashSS/Arasan integration. It programs controller configuration registers, optional top-level delay/DLL registers, clocks, reset control, UHS signaling, capability reads, and system sleep PM around the common `sdhci-pltfm` helper.

## Important APIs, Types, And Functions
`struct st_mmc_platform_data` stores reset control, optional interconnect clock, and optional top delay MMIO. `st_mmcss_cconfig()` programs FlashSS CCONFIG registers based on DT-compatible and MMC capabilities. `st_mmcss_set_static_delay()`, `st_mmcss_set_dll()`, `st_mmcss_lock_dll()`, and `sdhci_st_set_dll_for_clock()` manage static/dynamic delay and DLL lock. `sdhci_st_set_uhs_signaling()` selects UHS mode bits and delay behavior. `sdhci_st_readl()` masks 3.0 V support from capabilities. Lifecycle functions are `sdhci_st_probe()`, `sdhci_st_remove()`, `sdhci_st_suspend()`, and `sdhci_st_resume()`.

## Control Flow
Probe gets the mandatory `mmc` clock, optional `icn` clock, optional reset control, deasserts reset, initializes an SDHCI platform host with ST quirks, parses MMC OF data, enables clocks, maps optional `top-mmc-delay`, stores clock/reset data, programs FlashSS CCONFIG for STiH407, adds the host, and logs host/vendor version. On failure it disables clocks and asserts reset. Remove delegates to `sdhci_pltfm_remove()`, disables clocks, and asserts reset.

UHS signaling first clears speed-mode bits, applies static delay for each high-speed mode, sets VDD 1.8 V for UHS/HS200 paths, invokes DLL setup/lock for SDR50/SDR104/HS200 when host clock exceeds 90 MHz, warns on lock failure, then writes host-control2. `st_mmcss_cconfig()` sets base clock frequency from `max-frequency`, marks eMMC slot type or configures card-detect output, and advertises SDR50/SDR104/DDR50 bits according to MMC caps.

## State And Persistence
Persistent state includes prepared clocks, reset-control state, optional top-delay mapping, and CCONFIG/delay registers. Suspend marks retune if needed, suspends host, asserts reset, and disables clocks. Resume reenables clocks, deasserts reset, reprograms CCONFIG, and resumes the host.

## Dependencies And Integration Points
The driver depends on `sdhci-pltfm`, reset framework, clock framework, OF properties/resources, and MMC capability parsing. It matches `st,sdhci` and contains a special compatibility path for `st,sdhci-stih407`.

## Risks
DLL lock waits up to one second using jiffies and only warns when UHS signaling cannot lock, so cards may later fail with data errors. Optional `top-mmc-delay` absence silently disables delay programming. Capability masking removes 3.0 V support in reads, which affects core voltage decisions. Resume must replay CCONFIG after reset or capabilities/delay behavior can be stale.

## Test Signals
Test STiH407 and generic ST compatible systems, max-frequency selection at 50/100/200 MHz, removable versus eMMC CCONFIG, SDR50/SDR104/DDR50 capability exposure, DLL lock success above 90 MHz, reset assertion/deassertion across suspend/resume, and host-version log after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-st.c -->

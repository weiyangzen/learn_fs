# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/tg3.c lines 10168-18436

## Purpose

This chunk covers the upper half of the Broadcom Tigon3 (`tg3`) Ethernet driver lifecycle: completing hardware initialization, opening and stopping the netdev, interrupt/MSI-X queue setup, periodic maintenance, ethtool and ioctl operations, self-tests, NVRAM/VPD/firmware discovery, PHY and ASIC invariant detection, PCI probe/remove, power management, shutdown, and PCI error recovery. It is the place where low-level register programming from earlier helper code is connected to Linux networking, PCI, DMA, hwmon, PTP, firmware, NVRAM, PHYLIB, and ethtool interfaces.

## Important APIs, Types, and Functions

- `struct tg3` is the central persistent device state. This chunk fills or consumes fields such as `pdev`, `dev`, `napi[]`, `hw_stats`, `fw`, `fw_needed`, `fw_len`, `fw_ver`, `board_part_number`, `link_config`, `eee`, `coal`, `bufmgr_config`, `grc_local_ctrl`, `mac_mode`, `rx_mode`, `tx_mode`, `dma_rwctrl`, `nvram_size`, `nvram_pagesize`, `nvram_jedecnum`, `pci_chip_rev_id`, `pci_fn`, queue counts, interrupt counts, timers, and many `tg3_flag()` feature/quirk bits.
- `tg3_init_hw()` enables register access, waits for firmware, switches clocks, resets the memory window base, and delegates to `tg3_reset_hw()`. The beginning of the chunk is the tail of `tg3_reset_hw()`, programming buffer manager thresholds, descriptor-ring BDINFO blocks, DMA engines, coalescing, MAC modes, RSS, PHY setup, receive rules, APE heartbeat interval, and post-reset signatures.
- `tg3_start()`, `tg3_stop()`, `tg3_open()`, and `tg3_close()` implement the runtime netdev lifecycle. They allocate/free consistent DMA resources, initialize/finalize NAPI, request/free IRQs, initialize hardware, start/stop PHY, hwmon, timers, PTP, and carrier/queue state.
- `tg3_ints_init()`, `tg3_enable_msix()`, `tg3_request_irq()`, `tg3_test_interrupt()`, and `tg3_test_msi()` choose INTx/MSI/MSI-X, derive queue/vector counts, install handlers, and fall back from MSI to INTx if the generated interrupt test fails.
- `tg3_timer()` is the recurring maintenance loop. It detects missed MSI events, flushes posted writes for affected cores, handles non-tagged status races, checks WDMAC health, periodically fetches stats, enables EEE after deferred setup, polls link state for several hardware modes, sends ASF firmware heartbeats, and updates the APE heartbeat.
- Ettool callbacks are collected in `tg3_ethtool_ops`: register dumps, EEPROM reads/writes, link ksettings, WOL, message level, autoneg restart, ring sizing, pause, self-test, strings/stats, LED identify, coalescing, RSS indirection, channels, PTP timestamp info, and EEE.
- Netdev callbacks are collected in `tg3_netdev_ops`: open/stop, transmit, stats, address validation, multicast/promiscuous receive mode, MAC address, MII ioctl, TX timeout, MTU change, feature negotiation, netpoll, and hardware timestamp get/set.
- Self-test helpers include `tg3_test_nvram()`, `tg3_test_link()`, `tg3_test_registers()`, `tg3_test_memory()`, `tg3_run_loopback()`, `tg3_test_loopback()`, `tg3_self_test()`, `tg3_do_test_dma()`, and `tg3_test_dma()`.
- Discovery and invariant helpers include `tg3_detect_asic_rev()`, `tg3_get_invariants()`, `tg3_nvram_init()`, the chip-family-specific `tg3_get_*_nvram_info()` functions, `tg3_get_eeprom_hw_cfg()`, `tg3_phy_probe()`, `tg3_read_vpd()`, `tg3_read_fw_ver()`, `tg3_get_device_address()`, `tg3_calc_dma_bndry()`, `tg3_init_bufmgr_config()`, `tg3_init_coal()`, `tg3_phy_string()`, and `tg3_bus_string()`.
- PCI driver integration is completed by `tg3_init_one()`, `tg3_remove_one()`, PM callbacks `tg3_suspend()`/`tg3_resume()`, `tg3_shutdown()`, PCI AER callbacks `tg3_io_error_detected()`/`tg3_io_slot_reset()`/`tg3_io_resume()`, `tg3_err_handler`, and `tg3_driver`.

## Control Flow

Probe begins in `tg3_init_one()`: enable the PCI device, request BARs, allocate a multi-queue Ethernet netdev, initialize locks/work, map MMIO and optional APE registers, attach netdev/ethtool ops, then call `tg3_get_invariants()`. Invariants detect ASIC revision and board quirks, decide register access methods, initialize MDIO/NVRAM, read EEPROM/VPD/firmware versions, probe the PHY, set queue/ring capabilities, derive power/WOL/EEE/TSO/MSI features, and prepare coalescing and RX buffer geometry.

After invariants, probe configures DMA masks, buffer manager defaults, feature flags, MTU bounds, MAC address, NAPI mailbox layout, performs a defensive halt if firmware left DMA running, runs `tg3_test_dma()`, initializes coalescing and timers, registers the netdev, optionally registers PTP, logs discovered hardware, and saves PCI config state. Failure exits unwind APE mapping, main MMIO mapping, netdev allocation, PCI regions, and PCI enablement.

`ndo_open` runs `tg3_open()`: reject opens during PCI error recovery, load required firmware when needed, power up, clear init/interrupt state, and call `tg3_start()`. `tg3_start()` initializes interrupt mode and queue counts before allocating rings, initializes/enables NAPI, requests IRQs, notifies APE, initializes hardware, optionally verifies MSI delivery, starts PHY and hwmon, starts the timer, marks `INIT_COMPLETE`, enables interrupts, resumes PTP, starts TX queues, and reapplies loopback if requested.

`ndo_stop` runs `tg3_close()`: reject closes during PCI error recovery, call `tg3_stop()`, then prepare power-down and carrier-off if the PCI device is present. `tg3_stop()` cancels reset work, stops queues/NAPI-facing traffic, stops timer/hwmon/PHY, disables interrupts, halts hardware, frees rings, clears `INIT_COMPLETE`, frees IRQs, tears down MSI/MSI-X state, finalizes NAPI, and releases consistent DMA memory.

Configuration changes use a common stop/restart pattern. Ring changes, pause changes without PHYLIB, MTU changes, offline self-tests, suspend/resume, PCI error resume, and channel changes stop traffic or PHY as needed, take `netdev_lock()` and `tg3_full_lock()`, halt hardware, update `tp` fields, then call `tg3_restart_hw()`/`tg3_start()` and restore queues and PHY. `tg3_restart_hw()` also contains the failure path that closes the device if reinitialization cannot recover.

The timer runs under `tp->lock`, skips work while IRQ sync or reset work is pending, and always rearms itself after dropping the lock. It has fast-tick duties for interrupt/status race handling and one-second duties for stats and link maintenance. It is part of both correctness and liveness: missed MSI detection can synthesize an MSI handler call, and disabled WDMAC triggers reset work.

## State and Persistence Behavior

The driver persists hardware-derived facts in `tp` for the netdev lifetime: ASIC class flags, PHY flags, NVRAM properties, DMA workarounds, queue limits, offload capabilities, firmware names and version strings, board part number, WOL state, APE/ASF state, EEE configuration, coalescing settings, RSS indirection, RX/TX ring sizes, and MAC address. Many ethtool setters update only `tp` while down and defer hardware programming until the next open; while running, they program hardware immediately or restart it.

Statistics are accumulated across hardware resets. `tg3_periodic_fetch_stats()` copies 32-bit MAC/RCV counters into `struct tg3_hw_stats` high/low software counters. `tg3_get_estats()` and `tg3_get_nstats()` add current hardware counters to `estats_prev`/`net_stats_prev`. Per-queue drop counters live in each `struct tg3_napi` and are aggregated without full serialization, accepting small sampling races.

Firmware handling is persistent but lazy. `tg3_get_invariants()` sets `tp->fw_needed` for chips needing TSO, 5701 A0 patch firmware, or 57766 EEE firmware. `tg3_open()` requests firmware only when opening and adjusts capabilities if firmware is unavailable: 57766 disables EEE on firmware failure, older firmware TSO devices disable TSO, while 5701 A0 treats missing firmware as fatal.

NVRAM and EEPROM detection persists `NO_NVRAM`, `FLASH`, `NVRAM_BUFFERED`, `NO_NVRAM_ADDR_TRANS`, `PROTECTED_NVRAM`, `nvram_size`, `nvram_pagesize`, and `nvram_jedecnum`. Ettool EEPROM reads/writes use those values, temporarily override clocks/CPMU low-power modes, handle unaligned byte ranges by read-modify-write around 32-bit NVRAM accesses, and restore clock/CPMU state on exit.

Power-management state is coordinated through `INIT_COMPLETE`, carrier state, PHY flags, wakeup settings, and PCI power state. Suspend and shutdown cancel reset work, detach the netdev, stop hardware, and prepare power-down. Resume and PCI AER resume restore hardware using the same restart path used by runtime configuration.

## Dependencies and Integration Points

This chunk depends heavily on earlier `tg3.c` helpers for register I/O (`tr32`, `tw32`, mailbox writers), hardware reset/halt, ring allocation, TX/RX descriptor handling, PHY setup, NVRAM access, APE/ASF handshakes, PTP helpers, feature fixups, and interrupt handlers. It integrates those helpers into Linux subsystem entry points.

Kernel subsystem integrations include PCI probe/remove, PCI PM and AER, netdev ops, ethtool ops, NAPI/IRQ APIs, DMA mapping APIs, firmware loader, PHYLIB/MDIO, VPD parsing, hwmon registration, PTP clock registration, DMI quirks, device wakeup APIs, SSB Broadcom GigE helper APIs, and ACPI/DMI-visible shutdown behavior.

Hardware integration points include BAR0 MMIO, optional BAR2 APE MMIO, PCI config registers, NVRAM/EEPROM/OTP, NIC SRAM mailboxes, host coalescing/status/stat blocks, buffer manager pools, DMA engines, MAC/PHY registers, RSS hash/indirection registers, WOL/ASF/APE firmware mailboxes, and PTP timestamp registers.

## Risks and Edge Cases

- Hardware quirk density is high. Small changes to `tg3_get_invariants()` can alter register access methods, DMA boundaries, MSI support, TSO capability, PHY reset policy, or NVRAM interpretation for entire ASIC families.
- Locking order matters: many paths combine RTNL, `netdev_lock()`, `tg3_full_lock()`, `tp->lock`, timer cancellation, NAPI enable/disable, and work cancellation. Incorrect ordering can deadlock reset, close, suspend, self-test, and PCI error recovery paths.
- Restart paths intentionally drop and reacquire locks in `tg3_restart_hw()` while closing the device on fatal reinit failure. Callers must tolerate the netdev being closed under them.
- Ettool EEPROM writes can modify persistent device flash/EEPROM. The code validates magic and handles alignment, but test coverage should treat `set_eeprom` as destructive and hardware-specific.
- MSI fallback is delicate: `tg3_test_msi()` disables SERR, generates an interrupt, restores PCI command state, falls back to INTx on no interrupt, and resets hardware because the failed MSI can terminate with Master Abort.
- DMA setup has platform-specific behavior for 32/40/64-bit masks, HIGHMEM, PCI-X, cacheline boundaries, and old 5700/5701 corruption tests. Regressions may appear only on old PCI/PCI-X bridges or RISC platforms.
- Link handling differs across PHYLIB, internal PHY, SERDES, APE/ASF, CPMU polling, MI interrupt, and status-register polling. Misclassifying `phy_flags` can break autonegotiation, WOL, EEE, or link-change detection.
- The timer is part of recovery. Changes that delay or suppress it can hide missed MSI interrupts, stale WDMAC state, stats accumulation, ASF/APE heartbeats, and EEE enablement.
- PTP and hardware timestamping are only enabled for specific ASICs. `tg3_hwtstamp_set()` stores state even when down, but only writes RX timestamp control while running and enabled.
- Shutdown has a DMI-specific Dell PowerEdge restart AER quirk. Removing or broadening it can affect reboot reliability and PCIe error visibility.

## Test Signals

- Probe/remove: PCI device enables, BARs map, netdev registers, PTP registers on capable chips, logs show part number, revision, bus string, PHY string, features, and DMA mask. Failure-path tests should verify all resources unwind.
- Open/close: `ip link set up/down` should allocate/free IRQs and rings, start/stop timers and PHY, transition carrier correctly, and avoid reset-work races.
- Interrupt modes: MSI-X devices should expose expected RX/TX queue counts and RSS; MSI failure simulation should fall back to INTx without leaving stale IRQ/vector state.
- Ettool: `ethtool -i`, `-k`, `-S`, `-g/-G`, `-c/-C`, `-a/-A`, `-l/-L`, `-x/-X`, `--show-eee/--set-eee`, `-t online/offline`, `-p`, and EEPROM read paths exercise most callbacks in this chunk.
- MTU/offload: switching between standard and jumbo MTUs should update `JUMBO_RING_ENABLE`, restart hardware while running, and keep TSO behavior correct on 5780-class and jumbo-capable chips.
- NVRAM/VPD/firmware: boards with legacy EEPROM magic, selfboot firmware formats, protected NVRAM, no NVRAM, APE/DASH/NCSI, and 5762 OTP should produce sane `fw_ver`, board part number, NVRAM size, and capability flags.
- DMA: `tg3_test_dma()` at probe is the primary built-in signal. Regression tests need 32-bit, 40-bit, and 64-bit DMA configurations plus old PCI/PCI-X hardware where possible.
- Power/error recovery: suspend/resume, shutdown/restart, PCI AER recovery, and permanent error paths should stop queues/timers, detach/attach netdev, restore PCI state, restart hardware, and clear `pcierr_recovery`.
- Statistics: counters should continue monotonically across reset/restart where `*_prev` accumulation applies; CRC errors on 5700/5701 copper use PHY counters rather than MAC stats.

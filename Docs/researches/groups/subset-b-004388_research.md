# Research Group subset-b-004388

This grouped report covers the requested Calxeda XGMAC and Cavium Ethernet/LiquidIO files. Each file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/xgmac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/xgmac.c

## Purpose
This is a complete Linux platform `net_device` driver for the Calxeda Highbank 10G XGMAC block. It owns the MAC and DMA register programming, coherent descriptor rings, NAPI receive/transmit completion, multicast/unicast filtering, ethtool controls, hardware statistics, wake-on-LAN, suspend/resume, and OF platform binding for `calxeda,hb-xgmac`.

## Important APIs, Types, And Functions
Key local types are `struct xgmac_dma_desc`, `struct xgmac_extra_stats`, and `struct xgmac_priv`. The descriptor helpers initialize RX/TX rings, encode buffer lengths split across descriptor fields, manage ownership via `DESC_OWN`, and preserve end-of-ring flags. `xgmac_open()`, `xgmac_stop()`, `xgmac_xmit()`, `xgmac_poll()`, `xgmac_set_rx_mode()`, `xgmac_change_mtu()`, `xgmac_get_stats64()`, `xgmac_set_features()`, and `xgmac_set_mac_address()` form the `net_device_ops`. `xgmac_ethtool_ops` exposes link settings, pause parameters, stats strings, and wake-on-LAN configuration.

## Control Flow
`xgmac_probe()` claims the MMIO resource, allocates an Ethernet device, maps registers, detects the available perfect-address filters, requests the main and PMT IRQs, reads the initial MAC address, installs NAPI, and registers the netdev. `xgmac_open()` validates or randomizes the MAC address, resets and configures hardware, allocates DMA rings, fills RX descriptors with mapped SKBs, enables MAC/DMA, enables NAPI and queueing, and unmasks DMA interrupts. TX maps the skb head and fragments into consecutive descriptors, marks the first descriptor owned last to avoid DMA races, rings `XGMAC_DMA_TX_POLL`, and stops the queue when descriptor space is low. Interrupts acknowledge DMA status, collect abnormal-event counters, mask normal interrupts down to abnormal-only while NAPI runs, and schedule NAPI. NAPI reclaims completed TX descriptors, receives packets until budget, refills RX, completes NAPI, and restores the interrupt mask. TX timeout work disables NAPI and TX DMA, frees and reinitializes the TX ring, restarts DMA, and wakes the queue. Suspend disables interrupts and either arms PMT wake logic or fully disables MAC/DMA; resume clears PMT and re-enables DMA, interrupts, device attachment, and NAPI.

## State And Persistence
Runtime state is held in `xgmac_priv`: ring virtual/DMA addresses, SKB arrays, ring indices, flow-control flags, WOL options, IRQ numbers, NAPI, and software error counters. Hardware state is in XGMAC/DMA/MMC/PMT registers. No filesystem persistence is used. Statistics are partly hardware counters and partly in-memory software counters; `xgmac_get_stats64()` freezes MMC counters while reading. WOL choices persist only for the current driver lifetime and are applied to PMT registers during suspend.

## Dependencies And Integration Points
The driver integrates with the platform bus, OF match table, Linux netdev core, NAPI, ethtool, DMA mapping API, interrupt subsystem, PM sleep hooks, and netpoll when configured. It depends on MMIO accessors, coherent DMA, skbuff helpers, multicast/unicast address lists, and CRC32 hashing for hash filters.

## Risks
Risk centers on DMA ring correctness, ownership ordering, and descriptor-space accounting. RX assumes complete packets fit in one descriptor; fragmented RX descriptors are dropped. `xgmac_change_mtu()` stops and reopens the device in-place, so failures during reopen can leave the interface down. TX mapping failure cleanup must match exactly which fragments were mapped. Interrupt and NAPI ordering relies on barriers and mask writes. PMT wake enable toggles IRQ wake on `dev->irq` while the PMT interrupt is a separate IRQ, so platform wiring matters. The hardware init uses a fixed AXI bus magic value and no detailed feature negotiation beyond checksum support.

## Test Signals
Useful signals are successful platform probe and netdev registration; `ip link set up/down`; MTU changes up to 9000; TX/RX traffic with SG and checksum offload; multicast and unicast filter overflow into hash mode; NAPI interrupt rate under traffic; `ethtool -S`, pause parameter changes, RX checksum toggling, and WOL configuration; suspend/resume wake by magic or unicast; fault-injection for DMA mapping failure and TX timeout recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/calxeda/xgmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/Kconfig

## Purpose
This Kconfig file defines the Cavium Ethernet driver menu and the build-time configuration surface for Thunder NIC, BGX/RGX MAC blocks, the shared Cavium PTP clock, LiquidIO PF/core support, Octeon management Ethernet, and LiquidIO VF support.

## Important APIs, Types, And Functions
The important symbols are `NET_VENDOR_CAVIUM`, `THUNDER_NIC_PF`, `THUNDER_NIC_VF`, `THUNDER_NIC_BGX`, `THUNDER_NIC_RGX`, `CAVIUM_PTP`, `LIQUIDIO_CORE`, `LIQUIDIO`, `OCTEON_MGMT_ETHERNET`, and `LIQUIDIO_VF`. It has no C APIs, but these symbols gate compilation and module composition throughout `drivers/net/ethernet/cavium`.

## Control Flow
`NET_VENDOR_CAVIUM` opens the vendor subtree. The Thunder PF selects BGX; BGX and RGX select PHY/MDIO dependencies; Thunder VF implies `CAVIUM_PTP`. `CAVIUM_PTP` depends on PCI, 64-bit builds, and the PTP clock framework. `LIQUIDIO` selects `LIQUIDIO_CORE`, firmware loading, CRC32, and devlink; `LIQUIDIO_VF` selects `LIQUIDIO_CORE` and requires PCI MSI.

## State And Persistence
State is configuration metadata persisted in kernel `.config`. It affects whether objects are built-in, modules, or absent. It does not create runtime state.

## Dependencies And Integration Points
This integrates with the kernel Kconfig dependency resolver, module build rules, PCI, PHYLIB, MDIO, PTP, FW_LOADER, CRC32, NET_DEVLINK, and PCI_IOV/MSI-related runtime assumptions implied by the selected drivers.

## Risks
Misconfigured dependencies can produce missing shared objects or unavailable runtime features. `THUNDER_NIC_VF` only implies, rather than selects, `CAVIUM_PTP`; timestamp consumers must tolerate absent PTP support. `LIQUIDIO` redundantly depends on PCI through both `64BIT && PCI` and `PCI`.

## Test Signals
Run `make olddefconfig` and compile matrixes for built-in/module/disabled combinations, especially `LIQUIDIO_CORE` selected by PF and VF, `CAVIUM_PTP` absent with optional PTP users, and Thunder PF/BGX/RGX dependency closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/Makefile

## Purpose
This top-level Cavium Ethernet Makefile enters Cavium driver subdirectories when `CONFIG_NET_VENDOR_CAVIUM` is enabled.

## Important APIs, Types, And Functions
There are no runtime APIs. The important build rules append `common/`, `thunder/`, `liquidio/`, and `octeon/` to `obj-*` under the vendor symbol.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_NET_VENDOR_CAVIUM)` and recursively descends into the four Cavium subdirectories for enabled builds. Subdirectory Makefiles then decide individual object/module composition.

## State And Persistence
The file affects only build graph state. It has no runtime persistence.

## Dependencies And Integration Points
It integrates with Kbuild and the Cavium Kconfig menu. It assumes each listed subdirectory has its own Makefile and handles disabled internal symbols correctly.

## Risks
Because all Cavium subdirectories are entered under the vendor umbrella, broken disabled-code build rules in a subdirectory can still affect builds. Directory addition/removal must keep this file, Kconfig, and source tree in sync.

## Test Signals
Build with `CONFIG_NET_VENDOR_CAVIUM=y`, `m`, and disabled, and verify the common, Thunder, LiquidIO, and Octeon subtrees are only compiled as their nested symbols require.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/Makefile

## Purpose
This Makefile builds the shared Cavium PTP clock driver object when `CONFIG_CAVIUM_PTP` is enabled.

## Important APIs, Types, And Functions
The only build artifact is `cavium_ptp.o`, which exports `cavium_ptp_get()` and `cavium_ptp_put()` from `cavium_ptp.c`.

## Control Flow
Kbuild includes `cavium_ptp.o` in the built-in or module object list according to the tristate state of `CONFIG_CAVIUM_PTP`.

## State And Persistence
No runtime state is defined here; it controls object inclusion.

## Dependencies And Integration Points
It is reached through the Cavium top-level Makefile and depends on the Kconfig constraints for `CAVIUM_PTP`.

## Risks
Any Cavium network driver relying on PTP helpers must handle the Kconfig-disabled inline stubs in `cavium_ptp.h`; this Makefile does not force consumers to include the object.

## Test Signals
Build with `CAVIUM_PTP=y`, `m`, and disabled. Confirm module exports are present when enabled and consumers build against header stubs when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/cavium_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/cavium_ptp.c

## Purpose
This PCI driver exposes the Cavium/ThunderX PTP 1588 coprocessor as a Linux PTP hardware clock and provides exported reference-counted accessors for other Cavium network drivers that need to convert hardware timestamps.

## Important APIs, Types, And Functions
Public exports are `cavium_ptp_get()` and `cavium_ptp_put()`. PTP clock methods are `cavium_ptp_adjfine()`, `cavium_ptp_adjtime()`, `cavium_ptp_gettime()`, `cavium_ptp_settime()`, and `cavium_ptp_enable()`. Hardware-cycle integration uses `cavium_ptp_cc_read()`, `struct cyclecounter`, and `struct timecounter`. Probe/remove are `cavium_ptp_probe()` and `cavium_ptp_remove()`.

## Control Flow
Probe allocates `struct cavium_ptp`, enables the PCI device with managed PCI helpers, maps BAR0, initializes locking, cyclecounter, and timecounter, derives the coprocessor clock rate by probing the Cavium reset device and reading `RST_BOOT`, enables the PTP clock register, writes the compensation value, registers the PTP clock, and stores the clock pointer as PCI driver data. On failure, it stores an `ERR_PTR(err)` in driver data and returns success so consumers can distinguish failed initialization from an unprobed device. `cavium_ptp_get()` finds the PTP PCI function, returns `-ENODEV` if absent, returns `-EPROBE_DEFER` if driver data is not ready, and drops the PCI reference on errors. Remove unregisters the clock and clears the hardware enable bit.

## State And Persistence
State lives in `struct cavium_ptp`: PCI device reference, spinlock, MMIO base, clock rate, timecounter/cyclecounter, and registered PTP clock. Frequency adjustment is stored in the hardware compensation register; time adjustment is stored in the software timecounter. No data is persisted across driver unload or reboot.

## Dependencies And Integration Points
The file integrates with PCI, PTP clock framework, timecounter/cyclecounter helpers, MMIO `readq/writeq`, and Cavium reset-device registers. It exports symbols for other Cavium network drivers and matches specific Cavium subsystem IDs.

## Risks
The probe intentionally returns success on internal failures after storing an error pointer; code touching `pci_get_drvdata()` must use `IS_ERR_OR_NULL`. Clock-rate discovery probes a separate reset PCI device and falls back to `CLOCK_BASE_RATE * 16` if unavailable, which can skew timestamps. `cavium_ptp_adjfine()` performs fixed-point math and relies on spinlock serialization for register writes. `cavium_ptp_enable()` rejects ancillary features, so PPS/ext timestamp requests are unsupported.

## Test Signals
Load/unload the driver on supported PCI IDs; verify `/dev/ptp*` registration, `phc_ctl` get/set/adj operations, frequency adjustment behavior, consumers receiving `-EPROBE_DEFER` before readiness, and timestamp conversion stability under concurrent reads and adjustments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/cavium_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/cavium_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/cavium_ptp.h

## Purpose
This header declares the shared Cavium PTP clock object and provides enabled/disabled helper APIs for Cavium network drivers that use PTP timestamp conversion.

## Important APIs, Types, And Functions
`struct cavium_ptp` contains the PCI device, spinlock, cyclecounter, timecounter, MMIO base, clock rate, `ptp_clock_info`, and registered `ptp_clock`. When `CONFIG_CAVIUM_PTP` is reachable it declares `cavium_ptp_get()` and `cavium_ptp_put()`, defines `cavium_ptp_tstamp2time()` with locked `timecounter_cyc2time()`, and exposes `cavium_ptp_clock_index()`. When disabled, inline stubs return `-ENODEV`, `0`, or `-1`.

## Control Flow
Consumers call `cavium_ptp_get()`, use `cavium_ptp_tstamp2time()` to convert hardware cycle timestamps into nanoseconds, optionally query the PTP clock index, then call `cavium_ptp_put()`. Disabled builds compile through the same call sites without linking the PTP object.

## State And Persistence
The header describes in-memory and MMIO-backed clock state but does not allocate it. Timestamp conversion reads software timecounter state protected by `spin_lock`.

## Dependencies And Integration Points
It depends on `linux/ptp_clock_kernel.h` and `linux/timecounter.h` and is consumed by Cavium NIC drivers that need optional PTP support.

## Risks
Disabled stubs return plausible scalar values (`0` timestamp, `-1` index); callers must treat those as feature absence, not valid time. Consumers must balance `get`/`put` because the enabled accessor holds a PCI reference. Locking is internal to conversion, but lifetime is external.

## Test Signals
Compile with `CAVIUM_PTP=y/m/n`; verify consumers handle `ERR_PTR(-ENODEV)`, `-EPROBE_DEFER`, and successful conversion paths; validate reference cleanup on driver remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/common/cavium_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/Makefile

## Purpose
This Makefile defines the LiquidIO module composition for shared core code, PF driver code, and VF driver code.

## Important APIs, Types, And Functions
The build targets are `liquidio-core.o`, `liquidio.o`, and `liquidio_vf.o`. `liquidio-core-y` includes hardware-independent and chip-specific support such as `octeon_device.o`, `cn66xx_device.o`, `cn68xx_device.o`, `cn23xx_pf_device.o`, `cn23xx_vf_device.o`, mailbox, memory ops, DROQ, and NIC support. `liquidio-y` adds PF entry points and console/VF representor code; `liquidio_vf-y` adds the VF entry point.

## Control Flow
Kbuild first builds the selected core library object for `CONFIG_LIQUIDIO_CORE`, then links PF or VF front-end modules when `CONFIG_LIQUIDIO` or `CONFIG_LIQUIDIO_VF` are enabled.

## State And Persistence
No runtime state is defined here. It controls which object files are linked into each module.

## Dependencies And Integration Points
It is driven by Cavium Kconfig symbols. Both PF and VF support depend on the same core object, so shared chip setup code can be linked for either module.

## Risks
PF and VF chip-specific files are part of `liquidio-core.o`; exported symbols and function tables must avoid assuming that both PF and VF front ends are active. Build failures in any core object affect both PF and VF configurations.

## Test Signals
Build PF-only, VF-only, both, built-in, and module configurations. Confirm `liquidio` contains PF entry objects and `liquidio_vf` contains only VF entry objects plus shared core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_device.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_device.c

## Purpose
This file implements CN23XX Physical Function hardware setup for the LiquidIO core. It maps BARs, discovers PF/PCIe port identity, configures SR-IOV ring ownership, programs global input/output queue registers, manages PF/VF mailboxes, handles PF interrupts, exposes BAR1 index operations, and registers a CN23XX PF function table into `struct octeon_device`.

## Important APIs, Types, And Functions
External APIs are `setup_cn23xx_octeon_pf_device()`, `cn23xx_sriov_config()`, `cn23xx_pf_get_oq_ticks()`, `cn23xx_fw_loaded()`, `cn23xx_tell_vf_its_macaddr_changed()`, and `cn23xx_get_vf_stats()`. Key internal routines are `cn23xx_pf_soft_reset()`, `cn23xx_setup_global_mac_regs()`, `cn23xx_reset_io_queues()`, `cn23xx_pf_setup_global_input_regs()`, `cn23xx_pf_setup_global_output_regs()`, `cn23xx_setup_iq_regs()`, `cn23xx_setup_oq_regs()`, mailbox setup/free/thread helpers, interrupt handlers, and BAR1 helpers.

## Control Flow
`setup_cn23xx_octeon_pf_device()` validates BAR0/BAR1 assignment, maps both BARs, determines PF number from SR-IOV config or a firmware-populated fallback, computes SR-IOV ring layout, writes MAC credit count, fills `oct->fn_list`, installs register-address pointers, and stores the coprocessor clock rate. Device register setup enables PCIe error reporting, programs MAC-to-ring mapping, resets and configures PF-owned queues, configures output queues and backpressure, sets window timeout, and raises packet input jabber for VXLAN TSO. IQ/OQ setup writes descriptor base addresses, sizes, doorbell/count register pointers, and interrupt thresholds. Interrupt handling reads the PF interrupt summary, logs errors, dispatches VF mailbox interrupts, sets generic LiquidIO interrupt-status bits, and clears the summary. Mailbox paths allocate one mailbox per VF ring group, use delayed work for processing, poll on pre-1.1 revisions, and send PF-to-VF notifications or synchronous VF stats requests.

## State And Persistence
State is stored in `oct->chip` as `struct octeon_cn23xx_pf`, `oct->sriov_info`, `oct->fn_list`, `oct->mbox[]`, `oct->io_qmask`, queue structures, MMIO register pointers, and hardware CSR state. The driver persists no files. Firmware readiness is read from `CN23XX_SLI_SCRATCH2` unless multiple PF references imply firmware is already active.

## Dependencies And Integration Points
This file depends on LiquidIO core types (`octeon_device`, IQ/DROQ, mailbox, config), PCI config access, BAR mapping helpers, MMIO CSR helpers, SR-IOV configuration, versioned CN23XX register definitions, and kernel delayed work/vmalloc. Its function table is consumed by the generic LiquidIO core after chip detection.

## Risks
Ring reset polling uses bounded loops and can fail if QUIET/RST transitions do not match hardware expectations. SR-IOV ring partitioning assumes one ring per VF and CPU-count-based PF rings unless overridden. Mailbox allocation cleanup indexes `oct->mbox[i]` rather than the `q_no` used during allocation, which is worth reviewing when `rings_per_vf` is not one. `cn23xx_get_vf_stats()` waits up to one second and cancels mailbox queue `0` on timeout, which may affect unrelated outstanding mailbox work. `cn23xx_fw_loaded()` can intentionally return true from adapter refcount even before scratch status is set. Interrupt masks and mailbox behavior vary by revision.

## Test Signals
Test PF probe on CN23XX revisions 1.0, 1.1, and later; BAR mapping failure cleanup; SR-IOV enabled/disabled builds; PF/VF mailbox handshake, MAC-change notification, VF stats requests and timeout; MSI-X and non-MSI-X interrupt paths; queue enable/disable/reset; VXLAN TSO larger than default jabber; firmware-loaded race during multi-PF initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_device.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_device.h

## Purpose
This header declares CN23XX PF-specific LiquidIO state and exported setup/control APIs.

## Important APIs, Types, And Functions
`struct octeon_cn23xx_pf` stores PF interrupt summary/enable MMIO pointers, an interrupt mask, and a configuration pointer. `struct oct_vf_stats` defines the mailbox-returned VF counters. Function declarations cover PF setup, OQ tick conversion, SR-IOV configuration, firmware-loaded detection, VF MAC-change notification, and VF stats retrieval.

## Control Flow
The generic LiquidIO probe allocates the chip state and calls `setup_cn23xx_octeon_pf_device()`. After setup, generic code calls function pointers installed by the implementation and may call the declared helpers for SR-IOV and VF management.

## State And Persistence
The header defines in-memory state only. Interrupt pointers map BAR0 offsets, while `conf` references LiquidIO static/runtime configuration.

## Dependencies And Integration Points
It includes `cn23xx_pf_regs.h` and depends on `struct octeon_device`, `struct octeon_config`, and kernel integer types from the surrounding LiquidIO headers.

## Risks
The header exposes `struct oct_vf_stats` wire shape for mailbox transfer; producer and consumer must keep size within mailbox data capacity. Callers must ensure the PF chip state is initialized before using interrupt pointers or configuration.

## Test Signals
Compile PF and shared-core builds, validate `sizeof(struct oct_vf_stats)` fits mailbox payload, and exercise each declared exported symbol through PF initialization and SR-IOV operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_regs.h

## Purpose
This header defines the CN23XX PF PCI config offsets, BAR0 CSR offsets, queue register address macros, mailbox registers, DMA counters, MSI-X table layout, interrupt masks, BAR1 index registers, DPI registers, and reset registers used by the LiquidIO PF implementation.

## Important APIs, Types, And Functions
Important macro families include `CN23XX_SLI_IQ_*` for input queues, `CN23XX_SLI_OQ_*` for output queues, `CN23XX_SLI_PKT_MAC_RINFO64()` for PF/VF ring mapping, `CN23XX_SLI_PKT_PF_VF_MBOX_SIG()` and `CN23XX_SLI_MAC_PF_MBOX_INT()` for mailbox signaling, `CN23XX_SLI_MAC_PF_INT_*()` for PF interrupt summary/enable registers, `CN23XX_PEM_BAR1_INDEX_REG()` for BAR1 windows, and `CN23XX_DPI_*`/`CN23XX_RST_*` for DMA and reset programming. Bit masks describe ring enable/reset, endian/snoop/ordering behavior, interrupt status, and input/output thresholds.

## Control Flow
The header has no runtime control flow, but its macros are the address-generation layer used by CN23XX PF setup, queue programming, mailbox processing, interrupt handling, and reset routines.

## State And Persistence
It defines hardware register layout. State exists only in hardware CSRs and PCI config space when the driver uses these macros.

## Dependencies And Integration Points
It depends on kernel `BIT`/`BIT_ULL` definitions supplied through including translation units. It is consumed by `cn23xx_pf_device.c` and indirectly by the PF header.

## Risks
Register macros encode large offsets and stride assumptions; any mismatch corrupts queue or mailbox programming. Endian-dependent `CN23XX_PKT_INPUT_CTL_MASK` changes gather-list byte-swap behavior. The macro `CN23XX_INTR_PCIE_DATA` references `CN23XX_INTR_PKT_DAT`, which appears to be a typo for `CN23XX_INTR_PKT_DATA`; it is not used in the read PF implementation, but would break compilation if referenced. `CN23XX_INTR_ERR` and `CN23XX_INTR_MASK` intentionally select only subsets of possible interrupt bits.

## Test Signals
Build any code path that references every macro family, especially `CN23XX_INTR_PCIE_DATA`. Runtime validation should compare programmed queue, mailbox, BAR1, and interrupt addresses against CN23XX hardware documentation and exercise little- and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_pf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_device.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_device.c

## Purpose
This file implements CN23XX Virtual Function hardware setup for LiquidIO. It configures VF-visible queues, mailbox communication with the PF, PF/VF handshake, MSI-X interrupt decoding, queue enable/disable, and VF function-table registration.

## Important APIs, Types, And Functions
External APIs are `cn23xx_setup_octeon_vf_device()`, `cn23xx_octeon_pfvf_handshake()`, `cn23xx_vf_ask_pf_to_do_flr()`, and `cn23xx_vf_get_oq_ticks()`. Internal helpers reset queues, configure global input/output registers, setup IQ/OQ descriptors, setup/free the single VF mailbox, process mailbox work, handle MSI-X interrupts, update IQ read indices, and enable/disable output/input/mailbox interrupts.

## Control Flow
`cn23xx_setup_octeon_vf_device()` maps BAR0, reads PF number, VF number, and `rings_per_vf` from VF input-control register fields, clamps ring count against requested queues and CPU count, obtains CN23XX config, and installs VF function pointers into `oct->fn_list`. Device register setup resets VF queues and programs endian/order/snoop controls and thresholds. Mailbox setup builds one mailbox using VF read/write signal registers and writes the PF/VF signature. The handshake sends `OCTEON_VF_ACTIVE` with driver version, waits for the PF response, copies `pfvf_hsword`, pushes the PF-provided `pkind` into each IQ, and rejects major-version mismatches. MSI-X handling reads the DROQ packet-sent register, returns PO/PI bits, dispatches mailbox interrupt work for queue 0, and defers count clearing to read-index updates.

## State And Persistence
State lives in the shared `octeon_device`: VF number, PF number, `sriov_info.rings_per_vf`, `pfvf_hsword`, IQ/DROQ register pointers, mailbox object, and function table. Hardware queue state lives in VF BAR0 CSRs. No filesystem persistence exists.

## Dependencies And Integration Points
The file depends on LiquidIO core queue/mailbox/config abstractions, CN23XX VF register definitions, PCI BAR mapping helpers, MSI-X vector handling, delayed work, and PF cooperation through the mailbox protocol.

## Risks
The handshake waits in one-jiffy sleeps up to a large fixed count; PF absence or mailbox failure delays probe. `atomic_set(&status, 0)` happens after `octeon_mbox_write()`, so a very fast callback could be overwritten; this ordering deserves review. Input-interrupt enable/disable loops use `oct->num_oqs` while touching IQ registers, which is safe only if IQ/OQ counts match. Queue reset shares a single loop counter across queues. The VF relies on PF-programmed read-only fields for ring count and identity.

## Test Signals
Test VF probe with PF configured for different rings-per-VF values, CPU-count clamping, PF/VF handshake success and version mismatch, mailbox interrupt delivery, FLR request mailbox command, MSI-X PO/PI/mailbox bits, queue reset under traffic, and PF removal while VF waits for handshake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_device.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_device.h

## Purpose
This header declares CN23XX VF-specific LiquidIO chip state and public VF setup/mailbox helper APIs.

## Important APIs, Types, And Functions
`struct octeon_cn23xx_vf` stores the VF configuration pointer. Constants include `BUSY_READING_REG_VF_LOOP_COUNT` and `CN23XX_MAILBOX_MSGPARAM_SIZE`. Declarations cover PF-requested FLR, PF/VF handshake, VF device setup, and VF OQ tick conversion.

## Control Flow
The VF front end calls `cn23xx_setup_octeon_vf_device()` during chip setup, then the generic LiquidIO core uses installed function pointers. The PF/VF handshake helper is called to exchange readiness, version, and ring metadata with the PF.

## State And Persistence
The header defines in-memory state only. VF runtime state is kept in `octeon_device`, the mailbox object, and hardware CSRs.

## Dependencies And Integration Points
It includes `cn23xx_vf_regs.h` and assumes `struct octeon_device` and `struct octeon_config` are visible from LiquidIO core headers.

## Risks
The header keeps VF configuration minimal; callers must not expect PF-like interrupt pointer fields. Mailbox parameter size is fixed at six bytes and must match protocol users copying into `pfvf_hsword`.

## Test Signals
Compile VF-only and core builds, validate handshake message parameter sizing, and exercise all declared helpers under PF-present and PF-absent conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_regs.h

## Purpose
This header defines the VF-visible CN23XX PCI config offsets, queue CSR offsets, mailbox signal registers, interrupt bits, PTP/MIO registers, reset boot register, and MSI-X table layout.

## Important APIs, Types, And Functions
Important macros include `CN23XX_VF_SLI_IQ_*` and `CN23XX_VF_SLI_OQ_*` for queue programming, shared input/output control bit masks, `CN23XX_VF_SLI_PKT_MBOX_INT()` and `CN23XX_SLI_PKT_PF_VF_MBOX_SIG()` for VF mailbox communication, `CN23XX_VF_SLI_INT_SUM()` for per-queue interrupt summary, PTP register constants, and MSI-X table macros.

## Control Flow
There is no executable flow. `cn23xx_vf_device.c` uses the macros to reset queues, set descriptor ring bases, control queue enable bits, configure interrupt thresholds, and exchange mailbox messages with the PF.

## State And Persistence
State lives in hardware registers addressed by these macros. The header itself has no persistence.

## Dependencies And Integration Points
The header depends on `BIT`/`BIT_ULL` availability and is included through `cn23xx_vf_device.h`. It mirrors selected PF register definitions with VF-relative names and read-only comments for PF/VF identity fields.

## Risks
PF and VF headers duplicate many masks; divergence can break handshake and queue programming. Endian-dependent masks must match the PF and hardware. The header exposes PTP registers but the VF code read here does not directly use them, so unused definitions may drift.

## Test Signals
Compile VF builds on little- and big-endian configurations, verify register offsets against CN23XX VF hardware docs, and exercise queue, mailbox, interrupt, and MSI-X table accesses in VF probe and traffic tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_device.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_device.c

## Purpose
This file implements CN6XXX/CN66XX LiquidIO hardware setup shared with CN68XX. It handles soft reset, PCIe error/MPS/MRRS programming, coprocessor clock/tick conversion, global IQ/OQ register setup, queue register setup, queue enable/disable, BAR1 indexing, interrupt processing, register-address binding, CN66XX function-table setup, and CN6XXX config validation.

## Important APIs, Types, And Functions
Exported/common functions include `lio_cn6xxx_soft_reset()`, `lio_cn6xxx_enable_error_reporting()`, `lio_cn6xxx_setup_pcie_mps()`, `lio_cn6xxx_setup_pcie_mrrs()`, `lio_cn6xxx_coprocessor_clock()`, `lio_cn6xxx_get_oq_ticks()`, global IQ/OQ setup helpers, `lio_cn6xxx_setup_iq_regs()`, `lio_cn6xxx_setup_oq_regs()`, queue enable/disable, BAR1 helpers, `lio_cn6xxx_update_read_index()`, interrupt enable/disable, `lio_cn6xxx_process_interrupt_regs()`, `lio_cn6xxx_setup_reg_address()`, `lio_setup_cn66xx_octeon_device()`, and `lio_validate_cn6xxx_config_info()`. `lio_cn66xx_setup_iq_regs()` and `lio_cn66xx_setup_pkt_ctl_regs()` add CN66XX-specific backpressure and packet-control behavior.

## Control Flow
CN66XX setup maps BAR0/BAR1, initializes the DROQ interrupt-enable lock, installs function pointers into `oct->fn_list`, binds register-list pointers, loads `LIO_210SV` config, and stores the coprocessor clock rate. Device register setup configures PCIe MPS/MRRS, enables PCIe errors, writes global input routing, configures CN66XX packet control and global output registers, and sets a window timeout to avoid host hangs on invalid reads. IQ/OQ setup writes ring DMA addresses/sizes and stores doorbell/count register pointers. Queue enable manipulates global IQ/OQ enable masks; disable clears enable masks, waits for reset indication, resets doorbells/credits, and clears pending packet count/time interrupts. Interrupt processing validates the summary register, logs errors, processes DROQ count/time interrupts, sets generic LiquidIO interrupt status, and clears summary bits.

## State And Persistence
Runtime state is in `struct octeon_cn6xxx`, `oct->fn_list`, register-list pointers, IQ/DROQ structures, `oct->io_qmask`, `oct->droq_intr`, and hardware CSRs. No disk persistence is used. Read-index state uses the initial instruction counter saved in each IQ and handles 32-bit counter rollover.

## Dependencies And Integration Points
It integrates with LiquidIO core structures, CN66XX register macros, PCI config access, BAR mapping helpers, MMIO CSR helpers, DROQ packet checking, spinlocks, and generic interrupt status consumption by the core driver.

## Risks
Queue disable uses XOR to clear enable bits, which toggles bits and assumes masks are currently enabled. Polling reset waits have finite `HZ` loops and limited error reporting. Interrupt processing disables DROQ-specific interrupts under a spinlock when DROQ poll mode is active. PCIe MPS/MRRS values are ORed into DPI/SLI registers without clearing existing fields. Config validation covers queue counts, IQ instruction type, OQ refill threshold, and OQ time interrupt, but other config fields are trusted.

## Test Signals
Test CN66XX probe, BAR mapping failure cleanup, reset success/failure, MPS/MRRS configuration, IQ/OQ enable-disable cycles, DROQ interrupts in interrupt and poll modes, 32-bit instruction-count rollover, invalid config rejection, and traffic under packet/time interrupt coalescing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_device.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_device.h

## Purpose
This header declares CN6XXX/CN66XX LiquidIO chip state, PCIe MPS/MRRS enums, and common helper APIs shared by CN66XX and CN68XX implementations.

## Important APIs, Types, And Functions
`struct octeon_cn6xxx` stores interrupt summary/enable pointers, interrupt mask, configuration pointer, and a spinlock protecting DROQ interrupt-enable register access. `enum octeon_pcie_mps` and `enum octeon_pcie_mrrs` define PCIe payload/read-request settings. Function declarations cover reset, error reporting, PCIe tuning, global/queue setup, queue enable/disable, interrupt processing, BAR1, read-index updates, register binding, clock/tick conversion, CN66XX setup, and configuration validation.

## Control Flow
Chip setup files include this header to install common function pointers into `octeon_device`. CN68XX reuses most CN6XXX helpers while overriding reset and device-register setup.

## State And Persistence
The header defines in-memory chip state and function contracts only. Register pointers map BAR0; no persistent storage is involved.

## Dependencies And Integration Points
It depends on LiquidIO core types such as `octeon_device`, `octeon_config`, `octeon_instr_queue`, and `octeon_reg_list`, plus kernel IRQ and spinlock types from included compilation units.

## Risks
The common structure is used for multiple chip variants, so variant-specific fields must not be silently added without all setup paths initializing them. The MPS/MRRS enums use `-1` for default, so callers must pass the enum type and not unsigned storage.

## Test Signals
Compile CN66XX and CN68XX users, verify all declared functions are defined once in the core object, and test PCIe enum default and explicit values through setup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_regs.h

## Purpose
This header defines the CN6XXX/CN66XX LiquidIO register map: PCI config offsets, BAR0 window registers, IQ/OQ CSRs, global packet controls, DMA counters, interrupt masks, BAR1 index addresses, DPI registers, CIU reset registers, MIO/PTP registers, QLM/reset boot registers, and LMC reset constants.

## Important APIs, Types, And Functions
Macro families include `CN6XXX_SLI_IQ_*`, `CN6XXX_SLI_OQ_*`, `CN6XXX_DMA_*`, `CN6XXX_SLI_INT_*`, `CN6XXX_INTR_*`, `CN6XXX_BAR1_REG()`, `CN6XXX_DPI_*`, `CN6XXX_CIU_*`, and `CN6XXX_MIO_*`. It also defines endian-dependent `CN6XXX_INPUT_CTL_MASK` and composed masks for packet, DMA, PCIe-data, MIO, MAC, error, and total interrupt groups.

## Control Flow
There is no executable flow. CN66XX and CN68XX setup code uses these constants to program queue rings, interrupt coalescing, DPI, reset, BAR1 windows, and port routing.

## State And Persistence
State is represented by hardware registers addressed through the macros. The header contains no runtime allocation or persistence.

## Dependencies And Integration Points
The header depends on kernel bit macros and is included by CN66XX/CN68XX device implementation files. CN68XX-specific headers extend the map rather than replacing it.

## Risks
Stride and offset macros are central to DMA queue programming; incorrect use can corrupt unrelated CSRs. `CN6XXX_DPI_SLI_PRTX_CFG(port)` advances by `0x10` while separate constants show port0/port1 at `0x900` and `0x908`; this may reflect hardware layout or a suspicious stride and should be verified against documentation. Interrupt masks include broad error bits and data bits; handlers must clear exactly the bits they serviced. Endian-dependent input control must be validated on big-endian builds.

## Test Signals
Compile all users, compare generated addresses against hardware docs, exercise queue setup for multiple IQ/OQ indices, validate interrupt summary/mask behavior, BAR1 index programming, DPI setup, and reset register access on CN66XX hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_device.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_device.c

## Purpose
This file adds CN68XX-specific LiquidIO setup on top of the CN6XXX common helpers. It programs DPI FIFO/engine settings, overrides reset and device register setup, configures CN68XX packet pipe counts, applies a PCIe vendor-message filter workaround, detects 210NV versus 410NV card type, and installs the CN68XX function table.

## Important APIs, Types, And Functions
The exported entry point is `lio_setup_cn68xx_octeon_device()`. Internal helpers are `lio_cn68xx_set_dpi_regs()`, `lio_cn68xx_soft_reset()`, `lio_cn68xx_setup_pkt_ctl_regs()`, `lio_cn68xx_setup_device_regs()`, `lio_cn68xx_vendor_message_fix()`, and `lio_is_210nv()`.

## Control Flow
Setup maps BAR0 and BAR1, initializes the shared CN6XXX DROQ interrupt lock, installs mostly CN6XXX function pointers while overriding soft reset and device-register setup, binds register addresses with the common helper, detects card type from `CN6XXX_MIO_QLM4_CFG`, loads the matching config (`LIO_210NV` or `LIO_410NV`), stores coprocessor clock rate, and applies the vendor-message filter mask. Soft reset calls the CN6XXX reset, then programs DPI DMA control, disables DMA engines, sets FIFO sizes, and enables DPI. Device setup configures PCIe MPS default and MRRS 256B, enables errors, programs global input/output registers, writes CN68XX packet pipe count into `CN68XX_SLI_TX_PIPE`, configures backpressure, and sets the window timeout.

## State And Persistence
Runtime state is the shared `struct octeon_cn6xxx` chip state, function table, configuration pointer, BAR mappings, and hardware CSRs. No filesystem state is persisted.

## Dependencies And Integration Points
It depends on `cn66xx_device.c` helpers and `cn66xx_regs.h` for most register programming, plus `cn68xx_regs.h` for CN68XX-specific pipe/PKIND constants. It integrates with LiquidIO core chip detection and config lookup.

## Risks
DPI setup uses fixed FIFO sizes and disables engines before core setup; hardware revisions must match those assumptions. Card-type detection depends on one QLM config field. MPS/MRRS register writes share the common OR-style helpers. Setup failure after BAR mapping must unmap both bars; this path is covered when config lookup fails. Vendor-message workaround writes PCI config filter bits unconditionally for CN68XX.

## Test Signals
Test both 210NV and 410NV card detection, BAR mapping cleanup, DPI register programming after reset, MRRS 256B operation, packet pipe count matching configured OQs, backpressure on/off configs, vendor-message filter behavior, and inherited CN6XXX interrupt/queue operations under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_device.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_device.h

## Purpose
This minimal header declares the CN68XX LiquidIO setup entry point.

## Important APIs, Types, And Functions
The single public declaration is `lio_setup_cn68xx_octeon_device(struct octeon_device *oct)`, implemented in `cn68xx_device.c`.

## Control Flow
The generic LiquidIO chip-detection path calls this setup function for CN68XX devices. The function then installs CN68XX/common CN6XXX function pointers into `oct->fn_list`.

## State And Persistence
No state is defined in the header. CN68XX uses the common `struct octeon_cn6xxx` state from `cn66xx_device.h`.

## Dependencies And Integration Points
It depends on `struct octeon_device` being visible to including source files. It is included by the CN68XX implementation and any core code dispatching to CN68XX setup.

## Risks
The header intentionally does not expose CN68XX-specific state; callers needing common state must include the CN66XX/common header too. Missing prototype coverage would break chip dispatch.

## Test Signals
Compile chip dispatch and CN68XX implementation together and verify the setup symbol is exported from the shared LiquidIO core object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_regs.h

## Purpose
This header provides CN68XX-specific register definitions that supplement the mostly shared CN66XX/CN6XXX register map.

## Important APIs, Types, And Functions
It defines `CN68XX_SLI_IQ_PORT0_PKIND`, `CN68XX_SLI_IQ_PORT_PKIND(iq)`, `CN68XX_SLI_TX_PIPE`, and `CN68XX_INTR_PIPE_ERR`. `CN68XX_SLI_IQ_PORT_PKIND()` uses `CN6XXX_IQ_OFFSET`, so it is meant to be used with the common CN6XXX register header.

## Control Flow
There is no executable logic. The CN68XX setup implementation uses `CN68XX_SLI_TX_PIPE` to program output pipe count. Other macros are available for PKIND and pipe-error handling.

## State And Persistence
State is hardware register state only. The header does not allocate or persist anything.

## Dependencies And Integration Points
It depends on `CN6XXX_IQ_OFFSET` and kernel bit macros being available from surrounding includes. It extends CN66XX/CN6XXX register definitions for CN68XX-specific hardware blocks.

## Risks
Because the header relies on definitions from another header, include ordering matters unless translation units already include `cn66xx_regs.h`. `CN68XX_INTR_PIPE_ERR` is defined but not included in the common CN6XXX interrupt mask read here, so pipe-error handling may require explicit integration elsewhere.

## Test Signals
Compile CN68XX code with expected include order, validate `CN68XX_SLI_TX_PIPE` writes, and exercise or audit pipe-error interrupt handling if `CN68XX_INTR_PIPE_ERR` is expected to be surfaced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_regs.h -->

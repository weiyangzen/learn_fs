# subset-b-004412 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/dl2k.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/dl2k.c

Purpose: implements the PCI netdev driver for D-Link DL2000, Sundance/Tamarack IP1000A, and related gigabit Ethernet adapters. It binds devices from `rio_pci_tbl`, maps device registers, configures EEPROM-derived identity and PHY media, manages coherent descriptor rings, and exposes Linux `net_device` transmit, receive, ioctl, ethtool, interrupt, suspend, and remove operations.

Important APIs/types/functions: `rio_probe1` is the PCI probe path; `rio_open`/`rio_close` start and stop the interface; `start_xmit`, `receive_packet`, `rio_interrupt`, `rio_free_tx`, and `tx_error` implement the packet datapath and completion handling; `rio_hw_init`/`rio_hw_stop` program MAC, DMA, VLAN, coalescing, station address, statistics, and media controls; `parse_eeprom`, `read_eeprom`, `find_miiphy`, `mii_read`, `mii_write`, `mii_set_media`, `mii_get_media`, and PCS variants handle EEPROM and PHY/PCS management; `set_multicast`, `get_stats`, `clear_stats`, `rio_ioctl`, and ethtool link settings expose integration with the networking stack. The file depends on `struct netdev_private`, descriptor/register definitions, chip IDs, and PCI IDs from `dl2k.h`.

Control flow: module load registers `rio_driver` via `module_pci_driver`. Probe enables the PCI function, claims BARs, maps BAR0 for EEPROM and either BAR0 or BAR1 for MMIO when RMON is supported, allocates an `etherdev`, allocates coherent TX/RX rings, parses module parameters for media/MTU/VLAN/coalescing/flow control, reads EEPROM, finds a PHY, classifies copper versus fiber, and registers the netdev. Open allocates RX skbs and initializes descriptors, resets and programs hardware, requests a shared IRQ, starts the periodic RX recovery timer, starts the queue, then enables interrupts. Transmit maps the skb into a TX descriptor, applies optional VLAN insertion metadata, sets interrupt/coalescing flags, kicks DMA, advances `cur_tx`, and stops the queue when the ring is near full. Interrupt processing acknowledges status in a bounded loop, receives packets on `RxDMAComplete`, frees completed TX skbs on `TxDMAComplete` or driver-requested interrupts, and dispatches link/stat/host-error handling. Close disables queue and hardware, frees IRQ and timer, and unmaps/free skbs; remove unregisters the netdev and releases coherent rings, mappings, regions, and PCI state.

State and persistence behavior: persistent runtime state lives in `struct netdev_private`, including MMIO bases, descriptor rings, skb pointer arrays, DMA addresses, ring indices, locks, link/media settings, VLAN ID, coalescing values, flow-control flags, EEPROM name/LED mode, and RMON enablement. Module parameters (`mtu`, `vlan`, `jumbo`, `media`, `tx_flow`, `rx_flow`, `copy_thresh`, `rx_coalesce`, `rx_timeout`, `tx_coalesce`) influence initial device configuration but are not persisted. EEPROM contents provide MAC address, D-Link software-information cells, duplex/wake polarity, adapter name, and IP1000A LED mode. Statistics are accumulated into `dev->stats` by reading/acknowledging hardware counters under `stats_lock`; reading many counters also clears hardware state. Descriptor/skb ownership is transient and protected with `tx_lock`/`rx_lock` in completion/refill paths.

Dependencies/integration points: integrates with PCI core (`pci_enable_device`, `pci_request_regions`, `pci_iomap`, coherent DMA), netdev core (`net_device_ops`, `eth_hw_addr_set`, queue/carrier helpers, `netif_rx`), ethtool link settings, MII ioctl ABI, module parameters, PM sleep callbacks, DMA mapping APIs, CRC-based multicast hashing, and Linux MII constants. The file is tightly coupled to `dl2k.h` for hardware offsets and descriptors, and its legacy comments point users to `Documentation/networking/device_drivers/ethernet/dlink/dl2k.rst`.

Risks: descriptor arithmetic mixes wrapping modulo indices with unsigned ring counters, so queue stop/wake and timeout paths are sensitive to off-by-one or wrap behavior. RX allocation failure leaves descriptors temporarily unavailable and relies on the timer to recover exhausted rings. `dma_map_single` results in several refill paths are not always checked before reuse. Link-down transmit silently frees skbs while returning success. Hardware stats are clear-on-read, so concurrent or repeated readers can change accounting. Manual 1000 Mbps negotiation is deliberately constrained because 1000BASE-T requires autonegotiation. Legacy bit-banged MII and undocumented IP1000A PHY magic are hardware-sensitive. RMON devices map two BARs and use different EEPROM/MMIO bases, which increases probe/remove error-path risk.

Test signals: useful validation includes successful probe/remove with both RMON and non-RMON devices, `ip link set up/down`, IRQ receive/transmit under load, forced ring-full and TX timeout recovery, jumbo MTU and VLAN parameter behavior, multicast/promiscuous/allmulti filtering, link renegotiation through ethtool, MII ioctl reads/writes, suspend/resume while running, `ethtool -S`/`ip -s link` counter monotonicity, and DMA mapping fault injection for RX/TX allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/dl2k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/dl2k.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/dl2k.h

Purpose: defines the hardware contract and private driver state for the D-Link DL2000/IP1000A gigabit Ethernet driver implemented in `dl2k.c`. It contains register offsets, interrupt/MAC/DMA descriptor bit definitions, EEPROM layout, MII/PCS constants, ring sizing, private state, PCI device IDs, and MTU/timeout defaults.

Important APIs/types/functions: the central type is `struct netdev_private`, which holds RX/TX descriptor rings, skb arrays, coherent DMA addresses, PCI/MMIO pointers, spinlocks, media/VLAN/coalescing/flow-control state, ring indices, timer, PHY address, multicast filter, EEPROM-derived name and LED mode, and RMON enablement. `struct netdev_desc` is the 64-bit descriptor layout used by both TX and RX rings. `SROM_t` models the 256-byte EEPROM image consumed by `parse_eeprom`. `rio_pci_tbl` enumerates supported D-Link/Sundance device IDs and marks IP1000A devices via `CHIP_IP1000A`. Register enums such as `dl2x_offsets`, `IntStatus_bits`, `ReceiveMode_bits`, `MACCtrl_bits`, `TFC_bits`, and `RFS_bits` provide the constants used by MMIO accessors in the C file.

Control flow: this header has no executable control flow, but it shapes all control flow in `dl2k.c`: probe allocates rings sized by `TX_RING_SIZE`/`RX_RING_SIZE`; open initializes `netdev_desc` chains; transmit sets `TFC_bits`; receive checks `RFS_bits`; interrupt handling masks `IntStatus_bits`; hardware init programs `dl2x_offsets`, `ReceiveMode_bits`, and `MACCtrl_bits`; media negotiation uses MII and PCS enums; EEPROM parsing casts raw bytes to `SROM_t`.

State and persistence behavior: the header defines which driver fields are durable across netdev open/close while the PCI device remains bound. Ring memory, skb arrays, link state, PHY/media settings, LED mode, VLAN ID, and flow-control configuration persist in `netdev_private`; individual descriptor status/frag fields are volatile hardware-owned state. The EEPROM structure reflects persistent device data stored on the adapter, including MAC address, LED mode, software information block, and CRC.

Dependencies/integration points: includes kernel module, PCI, netdevice, etherdevice, skb, CRC32, ethtool, MII, I/O, uaccess, delay, timer, and spinlock headers. It exports `MODULE_DEVICE_TABLE` data for PCI modalias matching. It is consumed only in this driver family and must match hardware register layout exactly; build integration is through the parent D-Link Ethernet driver Makefile/Kconfig outside this work item.

Risks: register offsets and bit masks are hardware ABI and cannot be validated by the compiler. `struct netdev_private` embeds large skb arrays and assumes the ring constants match descriptor allocation sizes. Descriptor fields are little-endian and contain packed DMA address/length/status bits; incorrect masks can corrupt DMA. `TFC_bits` includes high-bit constants used in 64-bit descriptor status words, so accidental truncation would break VLAN or descriptor ownership. EEPROM parsing relies on `SROM_t` matching the card ROM layout and endianness.

Test signals: compile coverage catches missing kernel API types, but meaningful validation comes from `dl2k.c` runtime tests: ring initialization, descriptor ownership transitions, EEPROM CRC/MAC parsing, PCI ID autoloading, VLAN insertion, link negotiation, and stats reads. Sparse/endian checks are particularly useful because most hardware fields are `__le16`, `__le32`, or `__le64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/dl2k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/sundance.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/sundance.c

Purpose: implements the Linux PCI netdev driver for Sundance ST201 "Alta", D-Link DFE-5xx, and IC Plus IP100A Fast Ethernet adapters. It manages PCI discovery, EEPROM MAC loading, bit-banged MDIO, descriptor rings, tasklet-driven TX/RX bottom halves, link monitoring, ethtool/MII operations, Wake-on-LAN, suspend/resume, and device teardown.

Important APIs/types/functions: `sundance_probe1` is the PCI probe routine; `netdev_open`/`netdev_close` control interface lifetime; `init_ring`, `refill_rx`, `start_tx`, `tx_poll`, `rx_poll`, `intr_handler`, `reset_tx`, and `tx_timeout` implement data movement and recovery; `sundance_reset`, `eeprom_read`, `mdio_read`, `mdio_write`, `mdio_wait_link`, `check_duplex`, and `netdev_timer` configure hardware and media; `set_rx_mode`, `__set_mac_addr`, `sundance_set_mac_addr`, `get_stats`, `netdev_error`, and ethtool helpers expose netdev behavior. `struct netdev_private` contains ring pointers, skb arrays, coherent DMA addresses, tasklets, MII state, stats, locks, WOL state, and PCI/MMIO references.

Control flow: module initialization registers `sundance_driver`. Probe enables PCI, selects I/O versus MMIO BAR based on `CONFIG_SUNDANCE_MMIO`, maps registers, reads the MAC from EEPROM, allocates coherent TX/RX rings, initializes `mii_if_info`, registers netdev operations, scans MII PHY addresses, applies module media/flow-control overrides, resets the PHY/chip, and registers the device. Open resets hardware, requests IRQ, initializes rings and RX buffers, writes the RX list pointer and MAC/max-frame registers, configures multicast filters, starts the queue, resets TX, enables MAC engines, disables WOL for active operation, starts a link timer, and enables interrupts. The ISR acknowledges interrupts, disables RX DMA interrupts while scheduling the RX tasklet, handles TX statuses/completions and ring cleanup, wakes the queue when space returns, and delegates link/stats/PCI errors. RX tasklet drains up to a budget, handles errors, copies small packets if `rx_copybreak` is set, hands packets to `netif_rx`, refills descriptors, and reschedules itself if work remains. TX tasklet chains newly queued descriptors and starts hardware if needed. Close kills tasklets, disables interrupts/DMA/MAC, resets hardware, frees IRQ/timer, unmaps RX/TX skbs, and poisons RX addresses.

State and persistence behavior: per-device state persists in `netdev_private`: `cur_rx`/`dirty_rx`, `cur_tx`/`dirty_tx`/`cur_task`, `last_tx`, MII PHY IDs, media settings, flow-control and WOL flags, `xstats`, message level, and register base. Module parameters (`debug`, `rx_copybreak`, `media[]`, `flowctrl`) set initial behavior. Hardware counters are accumulated into `dev->stats` and `xstats` under `statlock`, and many counters clear when read. WOL configuration persists across suspend while `wol_enabled` is set; suspend closes the netdev and optionally leaves RX/WOL hardware armed. Descriptor/skb ownership is transient and coordinated among start_xmit, ISR, tasklets, and close through locks, tasklet serialization, and memory barriers.

Dependencies/integration points: integrates with PCI, coherent and streaming DMA APIs, Linux `net_device_ops`, ethtool ops, generic MII helpers (`mii_ethtool_*`, `generic_mii_ioctl`, `mii_link_ok`, `mii_nway_restart`), tasklets, timers, netpoll when configured, PM callbacks, module parameters, CRC multicast hashing, and WOL device wakeup APIs. The PCI ID table covers D-Link, Sundance, and IC Plus devices; `USE_IO_OPS` defaults to I/O BAR access unless MMIO is configured.

Risks: this is a legacy non-NAPI driver using tasklets and `netif_rx`, so high-rate RX can be sensitive to tasklet budget and interrupt masking. Several TX completion paths infer completed descriptors from hardware frame IDs and revision-specific status bits, which is fragile. Ring counters use unsigned deltas and modulo arithmetic; wrap and queue-full behavior should be treated carefully. RX/TX DMA mapping failures are handled by dropping/refill breakage but can reduce ring availability until later refill. Link and duplex updates are driven by timer/interrupt paths and bit-banged MDIO, making timing and PHY quirks important. WOL suspend reuses close/open paths and must preserve enough hardware state for wake. The driver contains old debug/error messages and hardware errata workarounds, including DFE-580TX-specific reset behavior.

Test signals: build with both `CONFIG_SUNDANCE_MMIO` choices where possible, probe each PCI ID family, bring interfaces up/down repeatedly, stress TX completion and queue stop/wake, test RX under small and large frames with `rx_copybreak`, validate MTU changes only when down, exercise multicast/promiscuous/allmulti filters, verify ethtool link settings and MII ioctl behavior, test WOL magic/link wake across suspend/resume, and inspect `ethtool -S` collision/broadcast/multicast counters after generated traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/sundance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ec_bhf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ec_bhf.c

Purpose: implements a PCI Ethernet-style netdev for the Beckhoff CX5020/CCAT FPGA EtherCAT master module. The driver maps CCAT information, EtherCAT, FIFO, MII, MAC, and DMA windows, allocates aligned coherent DMA buffers for hardware descriptor FIFOs, and polls TX/RX progress with a high-resolution timer instead of IRQ-driven NAPI.

Important APIs/types/functions: `ec_bhf_probe`/`ec_bhf_remove` bind and unbind the PCI device; `ec_bhf_setup_offsets` locates the EtherCAT master information block and derives subregion pointers and DMA channel IDs; `ec_bhf_open`/`ec_bhf_stop` allocate/free DMA buffers and start/stop polling; `ec_bhf_start_xmit` copies outgoing skb payloads into TX descriptors; `ec_bhf_process_rx`, `ec_bhf_process_tx`, and `ec_bhf_timer_fun` poll descriptor state; `ec_bhf_alloc_dma_mem`, `ec_bhf_setup_rx_descs`, `ec_bhf_setup_tx_descs`, `ec_bhf_add_rx_desc`, `ec_bhf_send_packet`, and `ec_bhf_reset` handle hardware-facing setup. Key types are packed `rx_header`/`rx_desc`, `tx_header`/`tx_desc`, `bhf_dma`, and `ec_bhf_priv`.

Control flow: probe enables the PCI device, sets 32-bit DMA mask, claims regions, maps BAR0 and BAR2, allocates an etherdev, marks the device `IFF_NOARP`, parses CCAT info blocks until `ETHERCAT_MASTER_ID`, reads the MAC from MII registers, and registers the netdev. Open resets MAC/FIFO counters, allocates RX DMA memory for 64 descriptors and registers each RX descriptor with the FIFO, allocates TX DMA memory for 64 descriptors, disables the MAC filter, marks TX descriptors sent, starts the netif queue, initializes the hrtimer, and starts periodic polling. Transmit copies skb data into the current TX descriptor, fills header length and port, writes FIFO TX register with aligned length/address, advances the TX index, and stops the queue if the next descriptor is not yet marked sent. The timer processes all received descriptors by allocating skbs and calling `netif_rx`, recycles RX descriptors, wakes TX queue when a stopped next descriptor becomes sent, and restarts while the netdev is running. Stop cancels the timer, resets hardware, disables TX, and frees coherent TX/RX allocations.

State and persistence behavior: `ec_bhf_priv` stores mapped BARs and derived subregion pointers, DMA channel numbers, RX/TX coherent allocation metadata, descriptor bases/counts/next indices, hrtimer state, and software byte counters. Hardware MAC counters are read live in `ec_bhf_get_stats`; byte counts are maintained in software and are not reset in `ec_bhf_open`, so they persist for the lifetime of the netdev across interface down/up. The module parameter `polling_frequency` is read-only at sysfs permission `0444` and controls hrtimer cadence in nanoseconds. Descriptor ownership is represented by hardware-updated packed header flags (`recv`, `sent`) in coherent memory.

Dependencies/integration points: integrates with PCI, 32-bit coherent DMA, MMIO accessors, hrtimer, netdev core, skb allocation/copy helpers, `eth_type_trans`, and basic Ethernet address helpers. The device is intentionally `IFF_NOARP`, fitting EtherCAT control traffic rather than ordinary IP Ethernet operation. It does not use IRQs, NAPI, phylib, ethtool, or standard MII helpers; hardware layout is discovered from CCAT info blocks.

Risks: RX packet length is trusted after masking and subtracting header/FCS sizes; malformed hardware descriptors could produce negative or nonsensical allocation sizes. TX uses `skb_copy_and_csum_dev` into a fixed descriptor payload without an explicit length guard against `PKT_PAYLOAD_SIZE`. Polling every 20 microseconds by default can cost CPU and introduces latency/throughput tradeoffs controlled by a global module parameter. Queue stop/wake depends on coherent visibility of `sent` flags and explicit memory barriers. DMA alignment is computed from a hardware mask by overallocating and choosing an aligned window; incorrect masks or 32-bit-only DMA constraints can fail device setup. `stat_rx_bytes`/`stat_tx_bytes` updates are not synchronized against stats reads.

Test signals: validate probe on CCAT hardware with a matching EtherCAT info block, open/stop cycles with DMA allocation fault injection, RX descriptor recycling under sustained EtherCAT traffic, TX queue stop/wake when descriptors are exhausted, oversized skb handling, timer cancellation during close/remove, `ip -s link` software byte and hardware packet/error counter behavior, and different `polling_frequency` values for CPU and latency impact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ec_bhf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/Kconfig

Purpose: defines the top-level Kconfig menu switch for Emulex Ethernet devices under the kernel networking drivers tree and includes the be2net-specific Kconfig when the vendor menu is enabled.

Important APIs/types/functions: `config NET_VENDOR_EMULEX` is a boolean menu option titled "Emulex devices"; it defaults to `y`, depends on `PCI`, and gates the nested `source "drivers/net/ethernet/emulex/benet/Kconfig"` inside `if NET_VENDOR_EMULEX`.

Control flow: Kconfig evaluation first checks PCI availability. If `NET_VENDOR_EMULEX=n`, all Emulex-specific driver prompts below this file are skipped. If enabled, the `benet/Kconfig` file contributes `BE2NET` and related chipset/HWMON options to the configuration UI.

State and persistence behavior: no runtime state. The selected boolean is persisted only in the kernel `.config` and controls which downstream symbols are visible and buildable.

Dependencies/integration points: integrates with the kernel Kconfig hierarchy and the `drivers/net/ethernet/emulex/Makefile`, where `CONFIG_BE2NET` later selects the `benet/` build directory. The dependency on `PCI` matches the hardware bus used by supported Emulex adapters.

Risks: disabling this vendor symbol hides be2net even if a user expects to select a specific card. The default `y` keeps prompts visible in PCI builds, but build output still depends on downstream tristate choices. The `source` path must remain aligned with the source tree location.

Test signals: run kernel configuration generation with `PCI=y` and `PCI=n`, verify `NET_VENDOR_EMULEX=n` hides `BE2NET`, verify `NET_VENDOR_EMULEX=y` exposes `benet/Kconfig`, and confirm `.config` plus Makefile produce or omit `drivers/net/ethernet/emulex/benet/` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/Makefile

Purpose: connects the top-level Emulex Ethernet driver directory to the kernel build system by descending into the BladeEngine/be2net subdirectory when `CONFIG_BE2NET` is enabled.

Important APIs/types/functions: the only build rule is `obj-$(CONFIG_BE2NET) += benet/`, which makes the `benet` subdirectory conditional on the be2net Kconfig tristate.

Control flow: during kbuild, if `CONFIG_BE2NET=y`, objects in `benet/` are linked into the built-in kernel image; if `CONFIG_BE2NET=m`, the subdirectory builds a module; if unset, the subdirectory is skipped.

State and persistence behavior: no runtime state. Build selection is persisted in `.config` through `CONFIG_BE2NET`.

Dependencies/integration points: depends on `drivers/net/ethernet/emulex/benet/Makefile` to name the actual be2net object and component objects. It is reached from the parent networking drivers Makefile when the Emulex vendor directory is included.

Risks: because the directory is keyed directly to `CONFIG_BE2NET`, adding any other Emulex driver would require extending this Makefile. A mismatch between Kconfig symbols and this rule would silently omit builds.

Test signals: build with `CONFIG_BE2NET=y`, `m`, and unset; confirm `benet/` is visited only for enabled cases and that the final built-in object or module includes be2net components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/Kconfig

Purpose: defines configuration symbols for the Emulex/ServerEngines BladeEngine OneConnect `be2net` Ethernet driver, optional HWMON thermal reporting, and compile-time support for BE2, BE3, Lancer, and Skyhawk chipset families.

Important APIs/types/functions: `config BE2NET` is the main tristate driver symbol and depends on `PCI`. `config BE2NET_HWMON` enables thermal sensor exposure when both `BE2NET` and `HWMON` are available and prevents a built-in driver from depending on modular HWMON. `config BE2NET_BE2`, `BE2NET_BE3`, `BE2NET_LANCER`, and `BE2NET_SKYHAWK` are boolean chipset-family gates, each depending on `BE2NET` and defaulting to `y`. The final warning comment is visible if all chipset gates are disabled while `BE2NET` remains enabled.

Control flow: selecting `BE2NET` makes the driver buildable. The optional chipset booleans affect preprocessor branches in `be.h` and implementation files, such as whether `BE2_chip`, `BE3_chip`, `lancer_chip`, or `skyhawk_chip` can match devices. HWMON selection controls compilation/registration of temperature reporting paths in the driver.

State and persistence behavior: no runtime state is stored here. User choices persist in `.config` and shape the compiled driver feature set. Disabling all chip families can produce a built driver with no useful device support, which is explicitly warned about.

Dependencies/integration points: integrates with kbuild through `emulex/Makefile` and `benet/Makefile`, with Linux PCI support, HWMON core, and compile-time conditionals in `be.h`/be2net sources. The HWMON dependency `!(BE2NET=y && HWMON=m)` prevents invalid built-in-to-module references.

Risks: chipset booleans compile out device-family detection macros; an overly trimmed config can leave expected adapters unsupported. The warning is advisory only and does not prevent building a useless driver. HWMON default `y` may add sysfs sensor exposure when available, so thermal paths need to compile under both built-in and module combinations.

Test signals: generate configs for `BE2NET=y/m`, with each chipset option toggled, and ensure PCI ID matching and chip macros compile. Validate all-chipsets-disabled shows the warning. Build combinations of `BE2NET=y/m` with `HWMON=y/m/n` to confirm dependency constraints and HWMON code selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/Makefile

Purpose: defines the kbuild object composition for the Emulex/ServerEngines BladeEngine `be2net` network driver.

Important APIs/types/functions: `obj-$(CONFIG_BE2NET) += be2net.o` declares the final built-in or module object. `be2net-y := be_main.o be_cmds.o be_ethtool.o be_roce.o` lists the component objects linked into `be2net.o`.

Control flow: when kbuild enters the directory with `CONFIG_BE2NET` enabled, it compiles the four component source files and links them into `be2net.o`. As a module, that object becomes `be2net.ko`; as built-in, it is folded into the kernel image.

State and persistence behavior: no runtime state. The object list is deterministic and controlled by `.config` only through `CONFIG_BE2NET`; this Makefile does not conditionally include or exclude HWMON/chipset objects, so those variations are handled inside source via preprocessor conditionals.

Dependencies/integration points: depends on `benet/Kconfig` for `CONFIG_BE2NET` and on source files `be_main.c`, `be_cmds.c`, `be_ethtool.c`, and `be_roce.c`. The resulting object uses shared headers such as `be.h`, `be_hw.h`, and `be_roce.h`.

Risks: any missing component object breaks the whole driver build. New functionality added in separate source files must be appended to `be2net-y`; otherwise it will not link. Since all current components are always linked, source-level conditionals must correctly guard optional HWMON, RoCE, and chipset behavior.

Test signals: run `make M=drivers/net/ethernet/emulex/benet` or a full kernel build with `CONFIG_BE2NET=m/y`, verify `be2net.o` links all four objects, and inspect `modinfo be2net.ko` for expected module metadata from the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/be.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/be.h

Purpose: provides the shared driver definitions for the Emulex/Broadcom `be2net` OneConnect/BladeEngine Ethernet driver. It declares device IDs, queue sizes, MTU/offload limits, DMA and queue abstractions, TX/RX/event/MCC/stat/resource structures, adapter-wide state, feature/chip macros, endian/bitfield helpers, packet classification helpers, error-state helpers, and cross-file function prototypes.

Important APIs/types/functions: `struct be_adapter` is the primary per-device state object, holding PCI/netdev pointers, BAR mappings, mailbox/MCC state, event queues, MSI-X entries, TX/RX queue arrays, statistics, work items, firmware versions, filter lists, VLANs, SR-IOV/VF state, RoCE state, resources, RSS, HWMON, VXLAN, WOL, PHY, error recovery, and private flags. `struct be_queue_info` abstracts DMA-backed queue head/tail/used/id state. `struct be_eq_obj`, `be_tx_obj`, `be_rx_obj`, and `be_mcc_obj` model event, TX, RX, and management command queues. `be_tx_stats`, `be_rx_stats`, `be_drv_stats`, `be_rx_compl_info`, `be_wrb_params`, `be_resources`, `be_vf_cfg`, `phy_info`, `rss_info`, `be_hwmon`, and `be_error_recovery` define datapath, capability, and management state. Inline helpers include queue index/node accessors, IRQ count calculators, AMAP bitfield get/set helpers, `swap_dws`, packet type checks, and error setters/clearers. Externs include `be_ethtool_ops`, `be_cq_notify`, `be_link_status_update`, `be_parse_stats`, `be_load_fw`, `be_update_queues`, `be_poll`, `be_eqd_update`, and RoCE add/remove/shutdown hooks.

Control flow: this header has no standalone execution, but it dictates how be2net implementation files share state. Queue helpers advance power-of-two ring indices and return head/tail nodes for producers/consumers. Chip-family macros are compiled according to `CONFIG_BE2NET_BE2`, `BE3`, `LANCER`, and `SKYHAWK`; disabled families cause their detection macros to evaluate false. IRQ helper functions derive needed RX/TX/combined interrupt counts from resource limits, RSS availability, MSI-X count, and CPU count. AMAP helpers manipulate hardware bitfield layouts used for completions and WRBs. Error helpers set adapter flags, drop carrier, and log link-down state for EEH, UE, firmware, TX, and hardware failures.

State and persistence behavior: all persistent runtime driver state is centralized in `be_adapter` and subordinate queue/stat/resource structures for the lifetime of the PCI-bound netdev. Queue heads/tails and atomics are live datapath state. Statistics use `u64_stats_sync` for lockless 64-bit updates. VLAN/filter lists and VF configuration persist until reconfiguration or removal. Firmware versions, serial numbers, resource limits, PHY state, and error recovery timestamps persist across open/close while the adapter object remains allocated. DMA memory descriptors track both virtual and bus addresses for mailbox, queues, stats commands, and filters.

Dependencies/integration points: includes PCI, Ethernet/netdev, IP/TCP/IPv6, VLAN, workqueue, interrupt, firmware, slab, `u64_stats_sync`, cpumask, and HWMON headers, plus local `be_hw.h` and `be_roce.h`. It integrates with ethtool via `be_ethtool_ops`, NAPI via `be_poll`, MSI-X and queue affinity, firmware mailbox/MCC command code, SR-IOV, RSS, VXLAN offloads, RoCE auxiliary support, HWMON thermal reporting, and kernel networking checksum/LSO/VLAN features. Kconfig chipset symbols directly affect matching helpers in this header.

Risks: the header is a high-fanout contract across be2net source files, so changing structure fields or queue constants can break TX/RX, firmware commands, ethtool, RoCE, or SR-IOV behavior. Ring helper `MODULO` asserts power-of-two limits with `BUG_ON`, making non-power-of-two queue lengths fatal. AMAP bitfield macros assume hardware structures are represented as bitfields with offsets divisible into 32-bit words; misuse can corrupt WRBs/completions. Packet helpers inspect IP headers and assume callers have valid network header setup. Chip macros compiled out by Kconfig can make supported hardware unreachable. Error helpers unconditionally turn carrier off and log link-down, so callers must avoid repeated noisy transitions.

Test signals: compile with each chipset Kconfig combination, big-endian builds for `swap_dws`, sparse/endian checking for DMA/hardware layouts, queue wrap tests around TX/RX/CQ/EQ lengths, ethtool stats and link tests, MSI-X/RSS channel scaling, SR-IOV VF configuration, firmware error recovery paths, RoCE enable/disable hooks on Skyhawk, HWMON temperature exposure, VXLAN offload configuration, and regression tests for MTU/GSO/VLAN limits defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/be.h -->

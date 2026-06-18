# Research: subset-b-004666

Grouped source research for Toshiba PS3 Gelic, Toshiba TC35815, and Tundra TSI108 Ethernet driver files. Each section preserves the source path and is intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_net.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_net.c

Purpose: Implements the PlayStation 3 Gelic wired Ethernet netdev and the shared card datapath used by the optional wireless netdev. It owns PS3 system-bus probe/remove, LV1 hypervisor DMA and interrupt setup, descriptor ring allocation, RX NAPI, TX queueing/completion, internal VLAN demultiplexing, multicast programming, link settings, and wake-on-LAN.

Important APIs and functions: Public/shared entry points are `gelic_card_set_irq_mask()`, `gelic_card_up()`, `gelic_card_down()`, `gelic_net_open()`, `gelic_net_stop()`, `gelic_net_xmit()`, `gelic_net_set_multi()`, `gelic_net_tx_timeout()`, `gelic_net_setup_netdev()`, `gelic_net_get_drvinfo()`, and `gelic_net_poll_controller()`. Core private helpers include descriptor status accessors, chain initialization/free/reset helpers, `gelic_descr_prepare_rx()`, `gelic_card_decode_one_descr()`, `gelic_descr_prepare_tx()`, `gelic_card_kick_txdma()`, `gelic_card_interrupt()`, `gelic_card_get_vlan_info()`, and PS3 driver `probe`/`remove`.

Control flow: Probe opens the PS3 hypervisor device, creates the DMA region, allocates an aligned `gelic_card` plus the Ethernet netdev, reads internal VLAN IDs, registers an interrupt status indicator, requests an event IRQ, maps TX/RX descriptor rings, preallocates RX skbs, registers the Ethernet netdev, then optionally probes wireless. Opening any Gelic netdev calls `gelic_card_up()`, which reference-counts users, enables the current IRQ mask, starts RX DMA at the RX chain head, and enables NAPI on the first user. TX uses `gelic_net_xmit()` under `tx_lock`: reclaim completed TX descriptors, obtain a free descriptor, optionally insert an internal VLAN tag, DMA-map the skb, link the descriptor into the hardware chain, and start LV1 TX DMA if not already active. The interrupt handler masks RX interrupts and schedules NAPI, reclaims TX and restarts any outstanding tail after TX chain-end interrupts, refreshes carrier on port-status changes, and delegates wireless virtual interrupts to `gelic_wl_interrupt()`. NAPI repeatedly decodes RX descriptors, selects Ethernet or wireless netdev by internal VLAN, drops error/oversize descriptors, passes good packets through GRO, refills the descriptor, relinks it at the chain tail, and restarts RX DMA if the hardware stopped at a chain end. Stop/down disables NAPI and DMA only when the last user closes.

State and persistence: Runtime state lives in `struct gelic_card`: shared `netdev[]`, IRQ status/mask, LV1 IDs, internal VLAN table, TX/RX descriptor chains, `tx_dma_progress`, timeout work, RX OOM timer, shared user count, link mode/status, and descriptor storage. Per-netdev stats are updated from TX/RX completions. No durable persistence is written, but wake-on-LAN state is mirrored through PS3 system-manager calls and the LV1 WOL filter state can persist across suspend/power behavior.

Dependencies and integration points: Depends on PS3 firmware feature detection, `ps3_system_bus_driver`, PS3 DMA/event-port helpers, LV1 network calls, Linux netdev/NAPI/ethtool APIs, DMA mapping, VLAN helpers, and optional `CONFIG_GELIC_WIRELESS`. The wireless netdev uses this file's card-level open/stop/TX/multicast/timeout operations and shares the same DMA and interrupt substrate.

Risks: Descriptor ownership is encoded in big-endian hardware fields and relies on `wmb()` before hardware visibility. RX release unmaps using `skb->len`, which is normally zero for fresh RX skbs, so mapping-size assumptions deserve scrutiny. Internal VLAN parsing reads the first two bytes of RX data and unknown VIDs are silently dropped after a log. `gelic_card_down()` keeps wireless interrupt bits enabled while stopping shared DMA, so ordering matters when wireless workqueues are active. Probe unwind has many staged PS3/LV1 resources; the status-indicator failure path should be checked because it passes `bus_id(card)` twice when clearing.

Test signals: Build with and without `CONFIG_GELIC_WIRELESS`; PS3 system-bus probe/remove; Ethernet open/close with multiple Gelic users; RX good, overlength, DMA error, unknown internal VLAN, RX OOM timer, and chain-end restart paths; TX checksum offload, internal VLAN insertion with low headroom, descriptor exhaustion/wake, LV1 TX kick failure, and watchdog restart; multicast/allmulti programming; link autoneg/speed/duplex ethtool changes; WOL enable/disable on supported and unsupported firmware; netpoll interrupt path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_net.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_net.h

Purpose: Defines the shared PS3 Gelic hardware contract and runtime data structures used by the wired and wireless Gelic netdevs. It captures descriptor counts, MTU/frame sizing, virtual interrupt bits, descriptor status/error bits, LV1 network control codes, internal VLAN identities, card/port abstractions, and shared datapath prototypes.

Important APIs and types: `struct gelic_hw_regs` is the packed hardware descriptor layout with payload, next-descriptor pointer, DMA command/status, result/valid sizes, and data status/error. `struct gelic_descr`, `struct gelic_descr_chain`, `struct gelic_card`, and `struct gelic_port` define the software view of descriptor rings, the shared adapter, and per-netdev private storage. Enums encode RX/TX descriptor status, descriptor DMA ownership states, LV1 control commands such as `GELIC_LV1_GET_MAC_ADDRESS`, `GELIC_LV1_SET_NEGOTIATION_MODE`, `GELIC_LV1_POST_WLAN_CMD`, and port/VLAN IDs. Inline helpers map netdevs and ports back to `gelic_card`, PS3 bus IDs, device IDs, and port-private data.

Control flow and integration: The header has no executable flow, but it is the ABI between `ps3_gelic_net.c` and `ps3_gelic_wireless.c`. Ethernet and wireless both embed `struct gelic_port` in their `net_device` private area, while wireless appends `struct gelic_wl_info` behind `gelic_port::priv`. The shared function declarations let wireless reuse Ethernet open/stop/TX/multicast/timeout/netpoll and driver-info logic.

State and persistence: `struct gelic_card` is the central mutable state: NAPI instance, both netdev pointers, RX OOM timer, aligned LV1 interrupt status, IRQ mask, PS3 bus device, internal VLAN table, TX/RX chains, TX lock and DMA progress flag, timeout work, waitqueue, up/down user reference count, cached Ethernet link status/mode, IRQ, and descriptor array. This state is runtime-only and reconstructed on probe; LV1 hardware state is controlled through IDs and masks stored here.

Dependencies and integration points: Pulls in Linux netdev, ethtool, DMA, skb, timer, mutex/spinlock, waitqueue, PS3 bus, and Gelic wireless declarations indirectly through users. Constants are tightly coupled to LV1 hypervisor ABI and Gelic firmware behavior.

Risks: Hardware fields are big-endian and packed; accidental host-endian access will corrupt descriptor ownership or sizes. Descriptor arrays require 32-byte alignment and `irq_status` requires 8-byte alignment, enforced in the C file with `BUILD_BUG_ON`. `port_priv()` depends on the flexible `long priv[]` layout, so appended private structures must preserve alignment. Misspelled legacy constants such as `RESPONCE` are ABI names and should not be "fixed" casually.

Test signals: Compile both Ethernet-only and wireless-enabled builds; validate descriptor alignment assertions; exercise all declared shared operations through Ethernet and wireless netdevs; verify internal VLAN routing constants against LV1 firmware on PS3; run sparse/endian checks over descriptor field usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_wireless.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_wireless.c

Purpose: Adds the optional PS3 Gelic/Eurus wireless netdev on top of the shared Gelic card. It exposes Wireless Extensions handlers, manages scan results and association policy, translates WEP/WPA/WPA2 settings into Eurus LV1 commands, handles wireless virtual interrupts, and registers/removes the `wlan%d` netdev when firmware and internal VLAN support are present.

Important APIs and functions: External entry points are `gelic_wl_driver_probe()`, `gelic_wl_driver_remove()`, and `gelic_wl_interrupt()`. Command machinery is centered on `gelic_eurus_sync_cmd_worker()` and `gelic_eurus_sync_cmd()`. Wireless Extension handlers cover name/range/scan/auth/ESSID/WEP/AP/encodeext/mode/nick and stats. Scan helpers include `gelic_wl_start_scan()`, `gelic_wl_scan_complete_event()`, IE synthesis/parsing/translation, and `gelic_wl_find_best_bss()`. Association helpers include `gelic_wl_try_associate()`, `gelic_wl_assoc_worker()`, `gelic_wl_do_wep_setup()`, `gelic_wl_do_wpa_setup()`, `gelic_wl_associate_bss()`, connected/disconnect event handlers, and netdev open/stop.

Control flow: Probe is gated by PS3 firmware >= 1.6 and a wireless internal VLAN. It allocates a wireless netdev whose private area contains `gelic_port` plus `gelic_wl_info`, creates single-thread command and event workqueues, initializes scan lists/completions/locks, installs shared Gelic netdev operations plus wireless handlers, registers the netdev through `gelic_net_setup_netdev()`, and enables wireless interrupt bits. User Wireless Extension calls update `gelic_wl_info` under `wl->lock` and may schedule association work. Association work starts or reuses a scan, waits for scan completion, filters the scan list by BSSID/ESSID/security, sends common config plus WEP/WPA config to Eurus, posts an ASSOC command, and waits for a connected event. Wireless interrupts complete command waiters or queue event work. Event work drains LV1 WLAN events; scan-complete retrieves GET_SCAN data and refreshes the cached list, deauth/beacon-lost disconnects, and connected/WPA-connected completes association and raises carrier.

State and persistence: `gelic_wl_info` stores cached BSS entries, scan state and age, command/event queues, status bit flags, auth/cipher/WPA selections, association state/completion, channel mask, WEP keys, PSK bytes/type, requested ESSID/BSSID, active BSSID, and `iw_statistics`. State resets on wireless stop, with no durable storage. Firmware state is manipulated through synchronous Eurus commands and may remain active until DISASSOC or driver removal.

Dependencies and integration points: Depends on `ps3_gelic_net.h` for shared card/port and TX/open/stop operations, PS3 LV1 net-control commands, Wireless Extensions, IEEE 802.11 constants, Linux workqueues/completions/timers, netdev carrier/events, and firmware-version checks for WPA2 and precise IE support.

Risks: The command worker waits indefinitely for `cmd_done_intr`; removal completes it, but lost command-complete interrupts during normal operation can stall the single command queue. WPA/RSN IE synthesis uses firmware security summaries when precise IEs are unavailable, which can select incorrect ciphers, especially WPA2 before firmware 2.2. Scan result parsing trusts firmware `size` progression within one page and needs robust bounds expectations. Association state uses both spinlocks and mutexes; disconnect events intentionally avoid completing `assoc_done`, relying on timeout. Stop cancels delayed work but event work is allowed to run after netdev down, so removal flush ordering is important.

Test signals: Wireless probe skipped for old firmware or missing VLAN; netdev register/remove; WEXT scan request and get-scan with fresh, stale, invalid-channel, and IE-bearing BSS entries; ESSID/BSSID filtering; WEP 40/104-bit setup and invalid key lengths; WPA/WPA2 PSK binary/passphrase setup and firmware-version gates; ASSOC success, timeout, command failure, deauth, beacon-lost, WPA error, and disconnect on stop/remove; RSSI stats while associated/unassociated; concurrent command/event completion during interface close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_wireless.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_wireless.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_wireless.h

Purpose: Defines the Gelic wireless/Eurus firmware ABI and the wireless private state consumed by `ps3_gelic_wireless.c`. It covers LV1 WLAN event IDs, Eurus command IDs and packed command payloads, scan result formats, wireless configuration state enums, scan/association state, and driver entry-point prototypes.

Important APIs and types: Event and command enums include `GELIC_LV1_WL_EVENT_*` and `GELIC_EURUS_CMD_*`. Packed firmware payloads include `struct gelic_eurus_common_cfg`, `gelic_eurus_wep_cfg`, `gelic_eurus_wpa_cfg`, `gelic_eurus_scan_info`, and `gelic_eurus_rssi_info`; all command fields are documented as big-endian. Driver-side state is held in `struct gelic_wl_info`, including scan lists, workqueues, completions, config bits, ciphers, keys, PSK, ESSID/BSSID, active BSSID, and Wireless Extensions stats. `struct gelic_eurus_cmd` carries one synchronous command through the workqueue. Inline helpers convert between `gelic_wl_info` and the enclosing `gelic_port`.

Control flow and integration: The header is included by both the shared Gelic net driver and the wireless implementation. `gelic_wl_driver_probe()` and `gelic_wl_driver_remove()` are called from PS3 Gelic probe/remove. `gelic_wl_interrupt()` is called from the shared IRQ handler when WLAN event or command-complete bits are present. The private ioctl constants provide pass-through PSK operations, though the C file mainly uses standard encodeext PMK handling.

State and persistence: The header defines runtime-only state. Scan cache entries own duplicated firmware scan blobs and are rotated between active/free lists. Config state flags track whether userspace provided ESSID, BSSID, PSK, WPA level, and channel info. Association state records disconnected/associating/associated and is coordinated with completions.

Dependencies and integration points: Depends on Linux Wireless Extensions and `iw_handler`, Linux list/completion/workqueue/spinlock primitives through users, and `ps3_gelic_net.h` for `struct gelic_port` layout. Firmware command structures must match the LV1/Eurus ABI exactly.

Risks: Packed big-endian firmware structures must be accessed with endian helpers. `gelic_eurus_scan_info` has a flexible `elements[]` tail, so consumers must validate `size` before parsing IE data. `gelic_wl_info` is appended after `struct gelic_port::priv`, so struct size/alignment changes affect netdev private layout. PSK/key buffers hold sensitive material and debug logging must not expose them.

Test signals: Compile wireless-enabled builds; validate structure sizes/packing against firmware expectations; scan result parsing with and without `elements[]`; state transitions for scan and association enums; private layout access through `wl_port()` and `port_wl()`; interrupt entry-point linkage from `ps3_gelic_net.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/ps3_gelic_wireless.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/tc35815.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/tc35815.c

Purpose: Implements the Toshiba TC35815 PCI 10/100 Ethernet driver, including PCI probe/remove, MMIO register programming, PHYLIB/MDIO support, TX/RX descriptor management, NAPI interrupt handling, CAM multicast filtering, ethtool stats, restart-on-error, and PCI power management.

Important APIs and functions: The netdev operations are `tc35815_open()`, `tc35815_close()`, `tc35815_send_packet()`, `tc35815_get_stats()`, `tc35815_set_multicast_list()`, `tc35815_tx_timeout()`, `phy_do_ioctl_running`, and optional netpoll. PCI lifecycle is `tc35815_init_one()` and `tc35815_remove_one()`. PHY support uses `tc_mdio_read()`, `tc_mdio_write()`, `tc_mii_init()`, `tc_mii_probe()`, and `tc_handle_link_change()`. Queue/data-path helpers include `tc35815_init_queues()`, `tc35815_clear_queues()`, `tc35815_free_queues()`, `tc35815_rx()`, `tc35815_poll()`, `tc35815_txdone()`, and `tc35815_check_tx_stat()`. Hardware setup/reset is handled by `tc35815_chip_reset()` and `tc35815_chip_init()`.

Control flow: PCI probe enables the device with managed PCI helpers, maps BAR 1, initializes netdev/NAPI/locks/work state, resets the chip, reads the MAC from PROM or platform fallback, registers the netdev, and registers/probes an MDIO bus. Open requests the shared IRQ, resets hardware, allocates a coherent descriptor area plus RX skbs, enables NAPI, initializes hardware registers/CAM/queues, starts PHY state, and starts the queue. TX maps one skb into one `TxFD`, stores the skb index in `FDSystem`, starts DMA if the ring was idle, stops the queue if full, and relies on completion interrupts/NAPI to reclaim. Interrupts mask through `DMA_IntMask` and schedule NAPI. Poll reads and clears `Int_Src`, handles fatal/recoverable conditions, calls RX up to budget, completes TX under lock, and unmasks interrupts when work is below budget. RX consumes controller-owned-complete frame descriptors, pulls the referenced free-buffer skb by BDID, unmaps and delivers good packets, updates error stats for bad packets, replenishes free-buffer descriptors, and returns RX frame descriptors to the controller. Fatal interrupts or TX timeout schedule restart work that resets hardware, clears queues, reinitializes, and restores CAM filters.

State and persistence: `struct tc35815_local` stores PCI/netdev/NAPI pointers, software stats, TX and RX locks, PHY bus/link state, restart work, coherent descriptor memory and DMA base, TX/RX descriptor cursors, free-buffer list state, skb/DMA handle arrays, message level, and chip type. Module parameters `speed` and `duplex` restrict advertised PHY modes. No durable persistence is written; PCI PM saves/restores device state around suspend/resume.

Dependencies and integration points: Uses Linux PCI, DMA coherent/single mapping, NAPI, PHYLIB/MDIO, ethtool, netdev CAM/multicast APIs, platform-device fallback for TX49xx MAC addresses, and optional PM/netpoll. Chip-specific behavior varies for TC35815CF, TC35815_NWU, and TC35815_TX4939.

Risks: Descriptor rings use little-endian ownership/control fields and `FDSystem` skb indexes; corruption can lead to BUG_ON or stale DMA unmaps. TX DMA mapping errors are not explicitly checked in `tc35815_send_packet()`. RX descriptor progression skips variable numbers of descriptors based on BD count and must stay synchronized with hardware `FDNext`. Fatal-error handling has a static counter that can eventually panic after repeated resets. Promiscuous mode is delayed until link because enabling it before link can hang some hardware. PM suspend resets hardware without freeing queue memory, so resume restart must preserve software descriptor allocations.

Test signals: PCI probe/remove for all device IDs; PROM MAC and platform fallback MAC; MDIO timeout and PHY attach failures; open allocation failure at coherent area and partial RX skb allocation; TX ring full/wake, idle restart, completion stats, underrun threshold escalation, and TX timeout restart; RX good, CRC/alignment/overflow/long/runt/error paths and RX budget exhaustion; FDA/BL/excess-BD and fatal interrupts; multicast, allmulti, promisc before/after link; ethtool stats and link settings; suspend/resume while running and while closed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/toshiba/tc35815.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/Kconfig

Purpose: Adds Kconfig menu entries for Tundra Ethernet devices and the TSI108 gigabit Ethernet driver.

Important APIs and symbols: Defines `NET_VENDOR_TUNDRA` as a vendor-menu boolean defaulting to `y` when `TSI108_BRIDGE` is available, and `TSI108_ETH` as a tristate driver option for Tundra TSI108 gigabit Ethernet ports. The help text documents that the module name is `tsi108_eth`.

Control flow and integration: Kconfig has no runtime flow. The vendor symbol gates visibility of the driver option through `if NET_VENDOR_TUNDRA`. The driver option is consumed by the local Makefile to build `tsi108_eth.o` and by source-level conditional compilation in the kernel configuration.

State and persistence: Kernel configuration persists in `.config`. Selecting `TSI108_ETH=y` builds the driver into the kernel; `m` builds a loadable module; `n` omits it.

Dependencies and integration points: Both symbols depend on `TSI108_BRIDGE`, tying this Ethernet support to platforms that expose the Tundra TSI108 bridge infrastructure and headers. It integrates with the broader Ethernet vendor menu.

Risks: Because `NET_VENDOR_TUNDRA` depends on `TSI108_BRIDGE`, the menu disappears entirely on non-TSI108 platforms. There are no extra dependencies on PHY/MII helpers here even though `tsi108_eth.c` uses MII APIs; those must be satisfied by surrounding kernel networking config selects.

Test signals: `oldconfig`/`menuconfig` visibility with and without `TSI108_BRIDGE`; built-in and module builds for `CONFIG_TSI108_ETH`; verify module name `tsi108_eth`; compile dependency coverage for MII, platform-device, and TSI108 register headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/Makefile

Purpose: Connects the Tundra Ethernet Kconfig option to the kernel build system.

Important APIs and definitions: The sole build rule is `obj-$(CONFIG_TSI108_ETH) += tsi108_eth.o`, so `tsi108_eth.c` is compiled when `CONFIG_TSI108_ETH` is built in or modular.

Control flow and integration: There is no runtime flow. Kbuild expands the `obj-*` assignment based on the resolved Kconfig value and links `tsi108_eth.o` into the built-in object list or module target.

State and persistence: The Makefile owns no state. The build artifact selection is derived from `.config`.

Dependencies and integration points: Depends on `drivers/net/ethernet/tundra/Kconfig` defining `CONFIG_TSI108_ETH` and on `tsi108_eth.c` plus its local/header dependencies being present in the same directory.

Risks: Any rename of `tsi108_eth.c` or Kconfig symbol must be reflected here. No subdirectory recursion or multi-object module composition exists, so adding helper files would require updating this Makefile.

Test signals: Compile with `CONFIG_TSI108_ETH=y`, `m`, and unset; verify built-in object or module generation; run `make M=drivers/net/ethernet/tundra` in module-capable configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/tsi108_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/tsi108_eth.c

Purpose: Implements the Tundra TSI108 gigabit Ethernet platform driver. It manages platform-provided register resources, MII/PHY polling, MAC setup, RX/TX descriptor rings, NAPI RX, TX completion, hardware statistics carries, multicast hashing, ethtool link settings, and platform-driver probe/remove.

Important APIs and functions: Netdev operations are `tsi108_open()`, `tsi108_close()`, `tsi108_send_packet()`, `tsi108_set_rx_mode()`, `tsi108_get_stats()`, `tsi108_do_ioctl()`, `tsi108_set_mac()`, and address validation. Interrupt/NAPI functions include `tsi108_irq()`, `tsi108_rx_int()`, `tsi108_tx_int()`, `tsi108_poll()`, `tsi108_complete_rx()`, `tsi108_refill_rx()`, and `tsi108_complete_tx()`. PHY/MII and timer helpers include `tsi108_read_mii()`, `tsi108_write_mii()`, `mii_speed()`, `tsi108_init_phy()`, `tsi108_kill_phy()`, `tsi108_check_phy()`, and `tsi108_timed_checker()`. Probe/remove are `tsi108_init_one()` and `tsi108_ether_remove()`.

Control flow: Probe obtains `hw_info` platform data, allocates a netdev/private state, ioremaps normal and PHY register windows, initializes `mii_if_info`, NAPI, netdev/ethtool ops, locks, resets MAC/PHY, reads or synthesizes a MAC address, initializes MAC registers, registers the netdev, and stores driver data. Open requests the platform IRQ, allocates coherent RX/TX rings, initializes descriptor next pointers and RX skbs, writes ring base registers, initializes PHY/autoneg, enables NAPI and a half-second timer, starts RX, unmasks relevant interrupts, enables MAC RX/TX, and starts the queue. TX validates PHY/link/ring space, maps the linear skb and frags into descriptors, marks SOF/EOF/interrupt/OWN bits, advances the head, opportunistically reclaims old TX descriptors, restarts TX DMA if idle, and stops the queue when low on descriptors. RX interrupts are masked and scheduled into NAPI; poll clears RX status, consumes completed descriptors up to budget, refills missing RX buffers, restarts RX DMA if idle, records errors, and unmasks RX interrupts when complete. The timer polls PHY media changes and schedules RX refill if memory pressure shrank the ring.

State and persistence: `struct tsi108_prv_data` stores MMIO bases, netdev/NAPI, platform IDs, PHY/IRQ/type, timer, RX/TX ring cursors and free counts, `rxpending`, link/duplex/speed/PHY status, coherent ring pointers/DMA addresses, skb arrays, TX/MISC locks, upper bits for hardware statistics counters, multicast hash cache, message level, MII state, and platform device pointer. State is runtime-only; hardware counters are folded into software high bits across carry interrupts and `get_stats()`.

Dependencies and integration points: Depends on platform data type `hw_info` and register macros from `<asm/tsi108.h>`/`tsi108_eth.h`, Linux platform-driver, DMA coherent/single and skb-frag DMA mapping APIs, MII helper library, timers, NAPI, netdev stats, ethtool, and multicast CRC hashing.

Risks: TX maps skb data and frags but does not unmap DMA mappings on completion/close in the visible code, which is a DMA lifetime risk unless platform DMA semantics make mappings identity/no-op. RX open initializes `buf0` with `virt_to_phys()` while refill uses `dma_map_single()`, creating inconsistent DMA API usage. `tsi108_init_phy()` initializes loop counter `i` to zero before `while (--i)`, effectively relying on unsigned wraparound for reset polling. PHY access is globally locked because both ports share PHY registers; lock ordering with `txlock`/`misclock` must remain stable. Remove unregisters and stops Ethernet but does not explicitly run close paths if resources are open beyond netdev core ordering assumptions.

Test signals: Platform probe with missing/malformed `hw_info`; ioremap failures; MAC read fallback and invalid MAC rejection; open partial RX/TX ring allocation failure; PHY init for BCM54xx and generic PHY, link up/down timer transitions, speed/duplex changes; TX link-down, ring-full, fragmented skb, interrupt-frequency batching, EOQ restart, and completion wake; RX good, bad/CRC/overrun, low-memory refill, budget exhaustion, pending continuation, queue restart; stat carry interrupt and concurrent `get_stats()`; multicast/allmulti/promisc hash programming; close/remove after active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/tsi108_eth.c -->

# Research: subset-b-004307

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_options.c -->
## sources/distributed-fs/ceph-client/drivers/net/bonding/bond_options.c

Purpose: this file is the central option table and mutation engine for the Linux bonding driver. It maps named options such as `mode`, `slaves`, `miimon`, `arp_interval`, `xmit_hash_policy`, `primary`, `queue_id`, and 802.3ad attributes onto parser tables, dependency checks, and setter functions that mutate `struct bonding` and `struct bond_params`.

Important APIs, types, and functions: the static `bond_opts[BOND_OPT_LAST]` table describes each `struct bond_option`, including display name, allowed values, unsupported modes, flags such as `BOND_OPTFLAG_RAWVAL`, `BOND_OPTFLAG_NOSLAVES`, and `BOND_OPTFLAG_IFDOWN`, and the concrete setter. Public helpers include `bond_opt_get_by_name()`, `bond_opt_get_val()`, `bond_opt_parse()`, `__bond_opt_set()`, `__bond_opt_set_notify()`, `bond_opt_tryset_rtnl()`, `bond_option_arp_ip_targets_clear()`, `bond_option_ns_ip6_targets_clear()`, `bond_slave_ns_maddrs_add()`, and `bond_slave_ns_maddrs_del()`.

Control flow: sysfs and netlink callers enter through `__bond_opt_set()` or `bond_opt_tryset_rtnl()`. The common path validates the option id, checks mode/slave/up-state dependencies, parses numeric or symbolic values, calls the option's setter, and translates failures into netdev logs and optional netlink extended acknowledgements. Setters then perform side effects: `mode` resets incompatible ARP settings and XDP/XFRM feature exposure, `miimon` and `arp_interval` cancel or queue delayed monitoring work, ARP/NS target setters update target arrays and per-slave last-RX slots, `slaves` delegates to `bond_enslave()` or `bond_release()`, and active/primary options trigger active-slave selection under netpoll blocking.

State and persistence: most state persists in `bond->params`, including mode, monitor intervals, ARP/NS target lists, primary name, LACP knobs, queue policy, all-slaves-active, and broadcast-neighbor settings. The file also updates RCU pointers for `primary_slave` and active slave selection, per-slave `queue_id`, `prio`, `inactive`, and IPv6 solicited-node multicast memberships. No on-disk persistence exists; values live for the lifetime of the bond device and are exposed via sysfs/netlink.

Dependencies and integration points: the file depends on `<net/bonding.h>`, RTNL serialization, RCU, delayed work, netpoll blocking, IPv4/IPv6 address parsing, neighbor-discovery multicast mapping, XDP compatibility checks, XFRM offload feature bits, 802.3ad update helpers, and core netdevice notifiers. It is the mutation backend for `bond_sysfs.c` and rtnetlink bond configuration.

Risks: incorrect dependency flags can allow mode changes while slaves are present or while the interface is up. Monitor interval changes must avoid leaving both ARP and MII timers active. Raw-value parsing is command-oriented for `+ifname`, `-ifname`, and `iface:queue`, so malformed strings can silently become `-EPERM` style user errors. IPv6 NS target changes alter multicast lists on backup slaves only in specific active-backup validation modes. Broadcast-neighbor uses a static key and must stay balanced when changed while up.

Test signals: useful signals are successful sysfs writes for every option, expected `-EBUSY`/`-ENOTEMPTY`/`-EACCES` failures, netlink extack text for invalid values, timer handoff between `miimon` and `arp_interval`, active-backup primary/active re-selection, ARP and NS target add/remove ordering, duplicate queue-id rejection, LACP setting propagation, XDP mode/hash compatibility, and correct netdevice `NETDEV_CHANGEINFODATA` notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_procfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/bonding/bond_procfs.c

Purpose: this file implements `/proc/net/bonding/<bond-name>` reporting. It presents a human-readable snapshot of bond-level settings, link monitoring status, ARP/NS targets, active/primary slave state, and per-slave status, including 802.3ad aggregator and LACP PDU details for privileged readers.

Important APIs, types, and functions: the seq-file iterator is `bond_info_seq_ops`, with `bond_info_seq_start()`, `bond_info_seq_next()`, `bond_info_seq_stop()`, and `bond_info_seq_show()`. Report rendering is split between `bond_info_show_master()` and `bond_info_show_slave()`. Lifecycle helpers are `bond_create_proc_entry()`, `bond_remove_proc_entry()`, `bond_create_proc_dir()`, and `bond_destroy_proc_dir()`.

Control flow: opening the proc file uses `pde_data()` to recover the `struct bonding` pointer. Iteration starts with `SEQ_START_TOKEN` for the master section and then walks slaves with `bond_for_each_slave_rcu()`. The show path prints the driver version, current bonding mode, optional fail-over MAC or transmit-hash policy, primary/current active slave details, MII and ARP monitor configuration, 802.3ad bond state, and then one slave block per slave. Creation happens per network namespace under `/proc/net/bonding`, and each bond creates a named proc entry when the bond appears.

State and persistence: this file does not own state beyond `bond->proc_entry` and `bond->proc_file_name`. It reads live bond and slave fields under RCU, including `curr_active_slave`, `primary_slave`, `params`, link status, speed, duplex, permanent hardware address, queue id, and LACP port/aggregator state.

Dependencies and integration points: it integrates with procfs, seq_file, network namespaces, `bond_net_id`, RCU slave iteration, capability checks via `capable(CAP_NET_ADMIN)`, and 802.3ad helpers such as `__bond_3ad_get_active_agg_info()` and `bond_3ad_churn_desc()`. The output depends on option lookup through `bond_opt_get_val()` for stable textual names.

Risks: output is a snapshot assembled while the bond is changing, so readers should tolerate transient `None`, `N/A`, or zero aggregator data. Privileged 802.3ad details are intentionally gated by `CAP_NET_ADMIN`; changes here can expose peer/system identifiers. Proc entry removal relies on the stored original file name, so rename handling must keep `proc_file_name` consistent.

Test signals: create and delete bonds across network namespaces, read proc output while enslaving/releasing devices, verify active-backup and 802.3ad sections, confirm capability-gated LACP fields are hidden from unprivileged readers, exercise ARP/NS target display, and validate cleanup after bond removal and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs.c

Purpose: this file exposes bonding control and status through sysfs. It creates `/sys/class/net/bonding_masters` per network namespace for creating/deleting bond devices and installs the per-bond `bonding/` attribute group that mirrors most user-visible options and status fields.

Important APIs, types, and functions: `bonding_show_bonds()` and `bonding_store_bonds()` implement the class attribute. `bonding_sysfs_store_option()` is the generic writer that maps an attribute name to a `bond_option` and calls `bond_opt_tryset_rtnl()`. The many `bonding_show_*()` functions expose option values and read-only status such as `mii_status`, `ad_aggregator`, `ad_num_ports`, `ad_actor_key`, `ad_partner_key`, and `ad_partner_mac`. Lifecycle hooks are `bond_create_sysfs()`, `bond_destroy_sysfs()`, and `bond_prepare_sysfs_group()`.

Control flow: writes to `bonding_masters` parse a leading `+` or `-`, validate the interface name, and call `bond_create()` or `unregister_netdevice()` under RTNL for deletion. Per-bond attribute writes duplicate the user buffer, resolve the option by attribute name, and delegate all parsing and mutation to `bond_options.c`. Show methods read `struct bonding` state, often under RCU for slave lists or active/primary pointers, format symbolic names through `bond_opt_get_val()`, and return empty output for mode-inapplicable privileged 802.3ad attributes.

State and persistence: the file owns no option state; it exposes live `bond->params`, RCU slave lists, carrier state, active aggregator info, and queue ids. It stores a copy of `class_attr_bonding_masters` inside `struct bond_net` so each namespace has its own sysfs file identity. Per-bond sysfs groups are attached through `dev->sysfs_groups[0]` before netdevice registration.

Dependencies and integration points: it depends on netdev class sysfs helpers, RTNL, namespace-aware sysfs file creation/removal, RCU, `bond_options.c`, `bond_create()`, `bond_enslave()`/`bond_release()` through the options backend, 802.3ad query helpers, and capability checks for sensitive LACP data.

Risks: sysfs writes use `rtnl_trylock()` through the option backend, so busy RTNL surfaces as `restart_syscall()`. Attribute names must stay aligned with `bond_opts[].name`, except aliases such as `num_grat_arp` and `num_unsol_na`. Show paths must fit into one page and use truncation markers for large slave lists. `bonding_masters` preserves legacy behavior by ignoring `-EEXIST`, which means repeated module loads can have partial class-control visibility.

Test signals: verify `+bond0` and `-bond0` through `bonding_masters`, per-namespace isolation, all per-bond option writes and reads, page-size truncation for many slaves, privileged and unprivileged reads of 802.3ad fields, active slave and primary updates under RCU, and successful sysfs cleanup on namespace and module teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs_slave.c -->
## sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs_slave.c

Purpose: this file adds read-only sysfs attributes to each bonding slave kobject. It gives per-slave visibility into active/backup role, MII status, link failure count, permanent hardware address, queue id, and selected 802.3ad operational state.

Important APIs, types, and functions: `struct slave_attribute` wraps a sysfs `struct attribute` and a slave-specific show callback. `SLAVE_ATTR_RO()` defines attributes for `state`, `mii_status`, `link_failure_count`, `perm_hwaddr`, `queue_id`, `ad_aggregator_id`, `ad_actor_oper_port_state`, and `ad_partner_oper_port_state`. `slave_sysfs_ops` routes generic kobject reads through `slave_show()`. Exported lifecycle helpers are `bond_sysfs_slave_add()` and `bond_sysfs_slave_del()`.

Control flow: slave creation calls `bond_sysfs_slave_add()`, which registers all files on `slave->kobj`. A read converts the kobject to `struct slave`, converts the attribute to `struct slave_attribute`, and invokes the stored callback. 802.3ad fields check bond mode and aggregator presence before returning numeric state; otherwise they return `N/A`.

State and persistence: no independent state is stored. The attributes reflect live `struct slave` fields: role from `bond_slave_state()`, link from `slave->link`, counters, `perm_hwaddr`, `queue_id`, and `SLAVE_AD_INFO(slave)->port` data. Aggregator lookup uses RCU where a pointer dereference needs protection.

Dependencies and integration points: it depends on the bonding slave kobject model, `to_slave()`, sysfs file creation/removal, RCU for aggregator access, and 802.3ad per-port state structures in `<net/bonding.h>`.

Risks: all attributes are read-only, but they still expose rapidly changing data without a global lock. Non-802.3ad modes must consistently return `N/A` for LACP fields. Queue id uses `READ_ONCE()` because option writes can update it concurrently.

Test signals: enslave and release devices while checking file creation/removal, read state transitions between active and backup, verify queue id changes after `bonding/queue_id` writes, confirm link failure counter increments, and validate 802.3ad `N/A` versus populated aggregator/port-state output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs_slave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/can/Kconfig

Purpose: this Kconfig file defines the top-level CAN device-driver menu. It enables the common CAN netdevice support, virtual interfaces, serial adapters, platform/PCI/SPI/USB controller families, bit-timing calculation, RX offload support, and debug logging.

Important APIs, types, and functions: the main symbols are `CAN_DEV`, `CAN_NETLINK`, `CAN_CALC_BITTIMING`, and internal `CAN_RX_OFFLOAD`. Driver symbols covered by this subset include `CAN_AT91`, `CAN_BXCAN`, `CAN_CAN327`, `CAN_C_CAN` via a sourced sub-Kconfig, and `CAN_CC770` via another sourced sub-Kconfig. It also sources the rest of the CAN driver family Kconfig files.

Control flow: once `CAN_DEV` is enabled, virtual drivers can be selected immediately. Hardware drivers are nested under `CAN_NETLINK`, which defaults to enabled and provides shared bittiming, restart, and error-state infrastructure needed by most CAN netdev drivers. Individual drivers add architecture, bus, and memory dependencies and select common helpers such as `CAN_RX_OFFLOAD`.

State and persistence: Kconfig state is build-time configuration. It determines whether drivers are built in, modular, or omitted, and whether debug builds add verbose device logging through the Makefile.

Dependencies and integration points: this file integrates with the kernel CAN core (`CAN`), TTY for serial line-discipline drivers, platform architecture symbols such as `ARCH_AT91` and `ARCH_STM32`, PCI for PCIe drivers, MFD dependencies for some board drivers, and `HAS_IOMEM` or `HAS_DMA` where MMIO or DMA is mandatory.

Risks: dependency mistakes can expose non-buildable drivers under `COMPILE_TEST` or hide valid hardware on supported architectures. `CAN_NETLINK` controls common behavior required by hardware drivers, so disabling it drops most physical controller options. Help text and module names need to stay aligned with actual Makefile targets.

Test signals: run Kconfig dependency checks for all relevant architecture combinations, verify modular names match built objects, confirm `CAN_RX_OFFLOAD` is selected by drivers that call rx-offload helpers, and test `CONFIG_CAN_DEBUG_DEVICES` adding `-DDEBUG` through the top-level Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/can/Makefile

Purpose: this Makefile maps CAN Kconfig symbols to built objects and subdirectories. It is the build fan-out for the CAN driver tree.

Important APIs, types, and functions: key targets in this subset are `obj-$(CONFIG_CAN_AT91) += at91_can.o`, `obj-$(CONFIG_CAN_BXCAN) += bxcan.o`, `obj-$(CONFIG_CAN_CAN327) += can327.o`, `obj-$(CONFIG_CAN_CC770) += cc770/`, and `obj-$(CONFIG_CAN_C_CAN) += c_can/`. Common subdirectories such as `dev/`, `esd/`, `rcar/`, `rockchip/`, `spi/`, `usb/`, and `softing/` are included with `obj-y`.

Control flow: kbuild includes this file after Kconfig resolution. Built-in and modular values on each `CONFIG_CAN_*` symbol decide whether corresponding objects or subdirectories are compiled into vmlinux, a module, or not built. `subdir-ccflags-$(CONFIG_CAN_DEBUG_DEVICES) += -DDEBUG` adds debug logging to all nested CAN driver compilations when enabled.

State and persistence: the file has no runtime state; it shapes build artifacts and compiler flags.

Dependencies and integration points: it must match symbol names in `drivers/net/can/Kconfig` and nested Kconfig files. Directory targets delegate object selection to sub-Makefiles such as `c_can/Makefile` and `cc770/Makefile`.

Risks: stale object mappings cause selected Kconfig symbols to produce no module or to compile unexpected code. `obj-y` subdirectories are always visited, so their own Makefiles must guard individual objects correctly. Debug flags apply broadly and can change log volume across all CAN drivers.

Test signals: run `make drivers/net/can/` with representative configs, verify module names for `at91_can`, `bxcan`, `can327`, `c_can`, and `cc770`, and check that `CONFIG_CAN_DEBUG_DEVICES=y` adds debug messages without build breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/at91_can.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/at91_can.c

Purpose: this is the SocketCAN netdevice driver for Atmel/Microchip AT91 SoC CAN controllers, including AT91SAM9263 and AT91SAM9X5 layouts. It programs controller bit timing, mailbox RX/TX layout, timestamped RX offload, CAN error reporting, optional transceiver PHY power, and a SAM9263-specific mailbox-0 filter sysfs knob.

Important APIs, types, and functions: `struct at91_priv` embeds `struct can_priv`, `struct can_rx_offload`, MMIO base, clock, PHY, TX head/tail counters, devtype data, and `mb0_id`. `struct at91_devtype_data` selects RX mailbox range and TX mailbox count. Main paths include `at91_setup_mailboxes()`, `at91_set_bittiming()`, `at91_chip_start()`, `at91_chip_stop()`, `at91_start_xmit()`, `at91_mailbox_read()`, `at91_irq_tx()`, `at91_irq_err_line()`, `at91_irq_err_frame()`, `at91_irq()`, `at91_open()`, `at91_close()`, `at91_set_mode()`, and `at91_can_probe()`.

Control flow: probe selects devtype from OF or platform id, obtains `can_clk`, maps MMIO, allocates a CAN netdev with echo slots matching the TX mailbox count, configures CAN bittiming and supported modes, attaches timestamped RX offload, optionally sets a PHY bitrate limit, and registers the netdev. Open powers the PHY, opens the CAN core, enables the clock, requests the shared IRQ, starts the chip, enables RX offload, and starts the queue. TX writes a frame into the current mailbox, handles ID/DLC/RTR/data registers, queues echo skb by mailbox index, advances priority-encoded `tx_head`, and enables that mailbox interrupt. IRQ service drains RX mailboxes through rx-offload, completes TX mailboxes in order, and emits error frames for state or protocol errors.

State and persistence: persistent runtime state is `tx_head`, `tx_tail`, current CAN state, RX offload queue state, mailbox configuration, and optional `mb0_id` used for disabled mailbox errata handling. Hardware state includes mode, bit timing, interrupt masks, mailbox IDs/masks/data/control, error counters, and timestamp registers. Close disables queue/offload, stops the chip, frees the IRQ, disables the clock, powers off the PHY, and closes the CAN core.

Dependencies and integration points: it depends on platform devices, OF compatibles `atmel,at91sam9x5-can` and `atmel,at91sam9263-can`, clocks, optional PHY transceivers, SocketCAN core, CAN error frames, rx-offload timestamp helpers, netdevice ops, ethtool timestamp info, and RTNL for `mb0_id` sysfs writes.

Risks: mailbox arithmetic differs by SoC and must match hardware errata, especially disabled mailbox 0 on SAM9263-style parts. The TX priority wrap logic intentionally stops the queue at counter wrap to preserve ordering. Some status bits are clear-on-read, so `reg_sr` accumulation in IRQ handling is important. Bus-off recovery is affected by hardware auto recovery and latched state bits. `mb0_id` writes are rejected while up and must mask SFF/EFF values correctly.

Test signals: probe both devtypes, validate bitrate programming and 3-sample/listen-only modes, transmit enough frames to wrap mailbox priority counters, receive timestamped frames and overflow error frames, force warning/passive/bus-off states, verify `mb0_id` sysfs behavior on SAM9263, and exercise open/close error paths for PHY, clock, and IRQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/at91_can.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/bxcan.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/bxcan.c

Purpose: this file implements the STM32 bxCAN SocketCAN driver. It handles MMIO controller registers, shared filter-bank configuration through a syscon regmap, RX FIFO offload, three TX mailboxes, state/error interrupts, bit timing, loopback/listen-only modes, and basic system sleep transitions.

Important APIs, types, and functions: `struct bxcan_priv` stores CAN private state, rx-offload, MMIO `struct bxcan_regs`, shared `gcan` regmap, IRQs, clock, config mode (`BXCAN_CFG_SINGLE`, `BXCAN_CFG_DUAL_PRIMARY`, `BXCAN_CFG_DUAL_SECONDARY`), RMW lock, TX head/tail, and timestamp. Key functions include `bxcan_enable_filters()`, `bxcan_chip_softreset()`, init/sleep mode helpers, `bxcan_mailbox_read()`, RX/TX/state-change IRQ handlers, `bxcan_chip_start()`, `bxcan_open()`, `bxcan_stop()`, `bxcan_start_xmit()`, `bxcan_do_set_mode()`, `bxcan_get_berr_counter()`, `bxcan_probe()`, and suspend/resume hooks.

Control flow: probe maps registers, resolves `st,gcan`, chooses primary/secondary/single filter layout from DT booleans, gets clock and named IRQs (`rx0`, `tx`, `sce`), allocates a CAN netdev with three echo slots, configures bittiming and supported modes, adds FIFO rx-offload, and registers the device. Open enables the clock, opens CAN core, enables rx-offload, requests three shared IRQs, starts the chip, and starts the queue. Chip start soft-resets the controller, leaves sleep, enters init, programs MCR/BTR, configures an accept-all filter for the selected bank, clears TX indices, leaves init, seeds the LEC field, and enables RX/TX/error interrupts. TX fills the next mailbox and starts transmission; TX IRQ consumes completion bits and echo skbs.

State and persistence: runtime state includes `tx_head`, `tx_tail`, CAN state, last RX timestamp, active filter bank, and clock state. Hardware state includes MCR/MSR/IER/ESR/BTR, TX/RX mailbox registers, FIFO release state, and global filter registers shared between bxCAN instances. Suspend sleeps a running device, detaches the netdev, marks state sleeping, and disables the clock; resume reverses that.

Dependencies and integration points: the driver depends on platform OF compatible `st,stm32f4-bxcan`, common clocks, `syscon_regmap_lookup_by_phandle()`, SocketCAN core, rx-offload FIFO helpers, bitfield helpers, iopoll polling, and named platform IRQ resources.

Risks: filter registers are shared between CAN instances, so primary/secondary DT properties must be correct. RMW locking protects local controller registers but not all global filter interactions beyond regmap serialization. Timestamping for error frames uses the most recent RX timestamp, not a dedicated error timestamp. Queue stop/wake depends on memory barriers around head/tail updates. Suspend/resume does not fully re-run `bxcan_chip_start()`, so hardware retention assumptions matter.

Test signals: validate single and dual-instance filter assignment, all three IRQs, loopback/listen-only/berr-reporting modes, TX ring full and wake behavior, FIFO RX parsing for SFF/EFF/RTR frames, bus warning/passive/bus-off and LEC error frames, bit timing limits, clock enable/disable, and suspend/resume while the interface is up and down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/bxcan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/Kconfig

Purpose: this Kconfig file defines build options for Bosch C_CAN/D_CAN controller support and its platform and PCI bus front ends.

Important APIs, types, and functions: `CAN_C_CAN` is the parent tristate for the shared core. `CAN_C_CAN_PLATFORM` enables directly attached platform devices. `CAN_C_CAN_PCI` enables PCI devices and depends on `PCI`.

Control flow: selecting the parent exposes child bus choices. The core object is built whenever `CAN_C_CAN` is enabled, while platform and PCI wrappers are optional and compile as separate objects/modules according to their symbols.

State and persistence: this is build-time state only. It controls which parts of the C_CAN stack are available in the kernel image or module set.

Dependencies and integration points: it depends on `HAS_IOMEM`, because both front ends ultimately use MMIO. The platform option covers ST and TI SoC integrations; the PCI option covers devices such as Intel EG20T/PCH and ST STA2X11.

Risks: enabling the parent without a bus wrapper builds the reusable core but no probing path. Missing PCI dependency would break non-PCI builds. Help text must stay aligned with supported compatibles and PCI IDs in the source files.

Test signals: Kconfig combinations should build the core alone, core plus platform, core plus PCI, and all as modules. `make oldconfig` should preserve sane prompts under `CAN_DEV` and `CAN_NETLINK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/Makefile

Purpose: this Makefile builds the Bosch C_CAN/D_CAN shared core and optional bus-specific front ends.

Important APIs, types, and functions: `obj-$(CONFIG_CAN_C_CAN) += c_can.o` builds a composite object from `c_can_ethtool.o` and `c_can_main.o`. `obj-$(CONFIG_CAN_C_CAN_PLATFORM) += c_can_platform.o` and `obj-$(CONFIG_CAN_C_CAN_PCI) += c_can_pci.o` add the platform and PCI wrappers.

Control flow: kbuild links `c_can_ethtool.o` and `c_can_main.o` into `c_can.o`, exporting shared helpers such as `alloc_c_can_dev()` and `register_c_can_dev()` for the wrappers. Bus wrappers compile only when their child Kconfig symbols are selected.

State and persistence: this file has no runtime state; it controls build composition and module contents.

Dependencies and integration points: symbol names must match `c_can/Kconfig`. The composite core must be available before platform/PCI wrappers can reference its exported functions.

Risks: object-list drift can omit the ethtool ops or core entry points from the module. Building wrappers without the parent would produce unresolved symbols, so Kconfig nesting and Makefile symbols must stay in sync.

Test signals: build `CONFIG_CAN_C_CAN=m` with each wrapper enabled/disabled, inspect that `c_can.ko` contains `c_can_main` and `c_can_ethtool` code, and run module dependency checks for wrapper modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can.h -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can.h

Purpose: this header is the shared contract for the Bosch C_CAN/D_CAN driver family. It defines abstract register ids, concrete register maps for C_CAN and D_CAN layouts, driver-data descriptors, RAM initialization metadata, TX ring state, private driver state, exported core APIs, and TX ring helpers.

Important APIs, types, and functions: `enum reg` names logical controller registers. `reg_map_c_can[]` and `reg_map_d_can[]` translate those names to offsets. `enum c_can_dev_id` differentiates `BOSCH_C_CAN` and `BOSCH_D_CAN`. `struct c_can_driver_data`, `struct c_can_raminit`, `struct c_can_tx_ring`, and `struct c_can_priv` carry device geometry, RAMINIT strategy, TX queue state, and all core callbacks. Exports declared here include `alloc_c_can_dev()`, `free_c_can_dev()`, `register_c_can_dev()`, `unregister_c_can_dev()`, and PM helpers when enabled.

Control flow: bus wrappers allocate a device with `alloc_c_can_dev()`, fill `struct c_can_priv` fields such as register map, read/write callbacks, clock frequency, base address, type, and RAMINIT hook, then call `register_c_can_dev()`. The core uses inline helpers `c_can_get_tx_head()`, `c_can_get_tx_tail()`, and `c_can_get_tx_free()` to manage TX ring capacity with different behavior for C_CAN prioritized mailboxes versus D_CAN FIFO-like transmission.

State and persistence: `struct c_can_priv` is the main runtime state object. It persists NAPI state, message object counts/ranges, RX mask, interrupt/status flags, TX direction bitmap, last status, TX ring indices, register accessors, MMIO base, type, RAMINIT system, and receive-command behavior.

Dependencies and integration points: the header is included by the core, ethtool file, platform wrapper, and PCI wrapper. It integrates with CAN core `struct can_priv`, NAPI, netdevices, regmap-backed RAMINIT, and architecture-specific MMIO access methods.

Risks: register map offsets and logical enum order must stay synchronized because 32-bit reads combine adjacent logical registers. TX free-space semantics differ by controller type and directly affect queue stopping. `struct can_priv` must remain first in `struct c_can_priv` for netdev private-data assumptions.

Test signals: compile C_CAN and D_CAN wrappers, verify register access paths on 16-bit and 32-bit aligned mappings, test TX ring wrap for both controller types, and use ethtool ring reporting to confirm message object partitioning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_ethtool.c

Purpose: this small file exposes C_CAN/D_CAN queue geometry through ethtool and provides generic timestamp capability reporting.

Important APIs, types, and functions: `c_can_get_ringparam()` fills `struct ethtool_ringparam` from `struct c_can_priv`, and `c_can_ethtool_ops` installs `.get_ringparam` and `.get_ts_info = ethtool_op_get_ts_info`.

Control flow: ethtool calls `get_ringparam`; the driver reports maximum RX/TX pending values as total message object count and current RX/TX pending values as the partition computed by `alloc_c_can_dev()`. Timestamp info is delegated to the standard netdevice helper.

State and persistence: no independent state exists. Output is derived from `msg_obj_num`, `msg_obj_rx_num`, and `msg_obj_tx_num` stored in `struct c_can_priv`.

Dependencies and integration points: this file depends on the shared C_CAN header, ethtool netlink/ioctl plumbing, and the netdevice private data initialized by the core.

Risks: the reported maximums are controller object counts rather than dynamically configurable rings. If the core changes message object partitioning, this reporting must remain consistent. It does not implement setters, so users cannot tune ring sizes through ethtool.

Test signals: `ethtool -g` should show expected RX/TX counts for 32-object and 64-object devices, and timestamp info should be available without hardware timestamp claims.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_main.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_main.c

Purpose: this file is the shared Bosch C_CAN/D_CAN SocketCAN core. It implements controller configuration, message object setup, TX/RX handling, NAPI polling, error-state reporting, runtime PM integration, RAM initialization control, netdevice operations, and exported allocation/registration helpers used by platform and PCI wrappers.

Important APIs, types, and functions: central functions include `c_can_obj_update()`, `c_can_setup_tx_object()`, `c_can_read_msg_object()`, `c_can_setup_receive_object()`, `c_can_start_xmit()`, `c_can_set_bittiming()`, `c_can_configure_msg_objects()`, `c_can_chip_config()`, `c_can_start()`, `c_can_stop()`, `c_can_do_tx()`, `c_can_do_rx_poll()`, `c_can_handle_state_change()`, `c_can_handle_bus_err()`, `c_can_poll()`, `c_can_isr()`, `c_can_open()`, `c_can_close()`, `alloc_c_can_dev()`, `register_c_can_dev()`, and optional `c_can_power_down()`/`c_can_power_up()`.

Control flow: wrappers call `alloc_c_can_dev()` to partition message objects into RX and TX halves, then register the netdev. Open runtime-resumes the device, initializes RAM, opens the CAN core, requests the shared IRQ, starts hardware, enables NAPI, enables interrupts, and starts the queue. Hardware interrupts disable controller IRQs and schedule NAPI. The poll path reads pending status, emits state-change and bus-error frames, drains RX message objects subject to quota, completes TX echo skbs, reenables IRQs if not bus-off, and finishes NAPI. TX setup writes IF registers, handles SFF/EFF/RTR frames and C_CAN direction changes, queues echo skb, and triggers or caches TX depending on ring position and controller type.

State and persistence: state lives in `struct c_can_priv`: NAPI, message object ranges, RX mask, `sie_pending`, `last_status`, TX ring, `tx_dir`, register accessors, RAMINIT hooks, and controller type. Hardware state includes IF1/IF2 command windows, message object validity/control/data, bit timing, control/test/status registers, interrupt masks, and optional D_CAN power-down state. PM helpers reset RAM and runtime-PM usage around open/close and suspend/resume.

Dependencies and integration points: the core depends on wrapper-provided MMIO callbacks and clock frequency, SocketCAN netdevice helpers, CAN error-frame helpers, NAPI, pinctrl active/sleep states, runtime PM, exported symbols for bus wrappers, and ethtool ops from `c_can_ethtool.c`.

Risks: IF command operations poll only briefly; slow or wedged hardware logs "Updating object timed out". RX polling intentionally handles gaps in pending bits to avoid reordering/losing messages, and comments warn against removing defensive checks. C_CAN TX objects are priority-based, while D_CAN has cached transmission handling at ring wrap. State-change handling must avoid reenabling IRQs after bus-off. PM power-down/up is D_CAN-specific and waits for PDA transitions with timeouts.

Test signals: validate 32-object and 64-object devices, SFF/EFF/RTR TX and RX, RX overflow error frames, NAPI quota behavior, interrupt disable/reenable, warning/passive/bus-off transitions and recovery notifications, berr-reporting on/off, loopback/listen-only modes, D_CAN software reset and power-down/up, runtime PM reference balance, and pinctrl state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_pci.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_pci.c

Purpose: this file is the PCI bus wrapper for the shared Bosch C_CAN/D_CAN core. It supports STMicroelectronics STA2X11 and Intel EG20T/PCH CAN devices, handling PCI enablement, BAR mapping, register alignment selection, optional MSI, and PCH soft reset.

Important APIs, types, and functions: `struct c_can_pci_data` describes controller type, message object count, register alignment, clock frequency, BAR, and reset callback. Register accessors cover 16-bit aligned, 32-bit aligned, and 32-bit access variants. `c_can_pci_probe()` and `c_can_pci_remove()` manage PCI lifecycle. `c_can_pci_reset_pch()` pulses the PCH soft-reset register.

Control flow: probe enables the PCI device, requests regions, tries MSI and bus mastering, maps the configured BAR, allocates a C_CAN netdev, fills `struct c_can_priv` with device pointer, IRQ, MMIO base, clock frequency, register map, accessors, type, and RAMINIT/reset callback, then calls `register_c_can_dev()`. Remove unregisters the CAN netdev, frees the core device, unmaps the BAR, disables MSI, releases regions, and disables the PCI device.

State and persistence: PCI-specific state is static per-device data in the ID table plus mapped BAR address stored in `priv->base`. Runtime controller state is owned by the shared core after registration. MSI state and requested PCI regions persist while the device is bound.

Dependencies and integration points: it depends on the PCI subsystem, ST and Intel PCI IDs, `alloc_c_can_dev()`/`register_c_can_dev()` from the core, register maps from `c_can.h`, and SocketCAN via the shared core.

Risks: register alignment must match the device or all logical register access breaks. MSI enable is opportunistic; shared IRQ operation must still work. PCH reset writes into an offset in the mapped BAR and assumes that BAR layout. Frequency is hardcoded in ID data and must match hardware clocking.

Test signals: probe/remove both supported PCI IDs, verify MSI and non-MSI interrupt handling, check bit timing against 50 MHz and 52 MHz frequencies, run loopback TX/RX, exercise PCH reset on open, and validate cleanup on failures after enable, region request, BAR map, allocation, and registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_platform.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_platform.c

Purpose: this file is the platform/OF wrapper for Bosch C_CAN and D_CAN controllers. It maps platform resources, selects C_CAN versus D_CAN register access, handles TI-specific RAMINIT through direct function registers or syscon regmaps, enables runtime PM, and wires suspend/resume for D_CAN power-down mode.

Important APIs, types, and functions: register accessors include 16-bit aligned, 32-bit aligned, and D_CAN 32-bit paths. RAMINIT helpers include `c_can_hw_raminit_syscon()` and `c_can_hw_raminit()`, protected by `raminit_lock`. Static driver data describes generic C_CAN, generic D_CAN, DRA7 D_CAN, and AM3352/AM4372 D_CAN message object counts and RAMINIT bits. Main lifecycle functions are `c_can_plat_probe()`, `c_can_plat_remove()`, `c_can_suspend()`, and `c_can_resume()`.

Control flow: probe reads match data, gets the clock, IRQ, and MMIO resource, allocates a C_CAN device with the configured object count, chooses register maps and accessors by controller id and resource memory type, configures RAMINIT from `syscon-raminit` when present for TI SoCs, fills base/device/clock/type, enables runtime PM, registers the shared C_CAN netdev, and leaves runtime operation to the core. Suspend detaches a running D_CAN netdev, calls `c_can_power_down()`, and marks the state sleeping; resume calls `c_can_power_up()`, restores error-active state, and reattaches/restarts the queue.

State and persistence: wrapper state is mostly `struct c_can_priv` fields set at probe: MMIO base, clock rate, register map/accessors, type, device pointer, and RAMINIT configuration. Syscon-backed RAMINIT state persists in `priv->raminit_sys` and uses shared register bits across CAN instances.

Dependencies and integration points: it depends on platform devices, OF match data (`bosch,c_can`, `bosch,d_can`, `ti,dra7-d_can`, `ti,am3352-d_can`, `ti,am4372-d_can`), clocks, resource flags, syscon/regmap, runtime PM, and the shared C_CAN core exported APIs.

Risks: `device_get_match_data()` must provide valid driver data; legacy platform-id matching depends on the driver table. TI RAMINIT sequences are sensitive to start/done bit semantics and the DRA7 pulse requirement. Shared syscon access needs locking to avoid cross-instance corruption. Suspend/resume is only meaningful for D_CAN and warns for C_CAN. Clock frequency is assumed stable after probe.

Test signals: probe generic C_CAN/D_CAN and TI variants, validate 16-bit versus 32-bit resource access, test `syscon-raminit` instance ids and timeout logs, run CAN traffic across suspend/resume, check runtime PM balance on open/close, and verify cleanup after registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/can327.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/can327.c

Purpose: this file implements the `N_CAN327` tty line discipline that exposes ELM327-based OBD-II adapters as a best-effort SocketCAN netdevice. It translates CAN frames to ELM327 ASCII commands, parses ASCII monitor output back into CAN frames, manages initialization scripts, and detects UART-side failures.

Important APIs, types, and functions: `struct can327` embeds `struct can_priv`, rx-offload state, fixed TX/RX buffers, a spinlock, tty/netdev pointers, TX work, RX/TX accounting, state-machine enum, command bitmap, cached CAN frame/config, parser flags, and `uart_side_failure`. Key functions include `can327_send()`, `can327_kick_into_cmd_mode()`, `can327_send_frame()`, `can327_init_device()`, `can327_parse_frame()`, `can327_parse_error()`, `can327_handle_prompt()`, `can327_parse_rxbuf()`, netdev ops, line-discipline receive/write-wakeup/open/close/ioctl handlers, and module init/exit registering the line discipline.

Control flow: opening the line discipline requires `CAP_NET_ADMIN`, a tty write op, allocates a CAN netdev, initializes tty and CAN metadata, stores `tty->disc_data`, and registers the CAN device. Netdev open opens CAN core, computes the ELM bitrate divisor, queues initialization/config/monitor commands, adds manual rx-offload, and starts the queue. TX stops the queue, records the outgoing frame and required CAN-ID/config changes in `cmds_todo`, kicks the adapter into command mode, and frees the skb after accounting. RX from tty appends validated characters into `rxbuf`, drives a state machine for dummy char, prompt, and monitor mode, parses completed CR-delimited lines as CAN frames or ELM error strings, and queues skbs through rx-offload. TX wakeups schedule work to flush partial tty writes.

State and persistence: runtime state is the line discipline instance, tty binding, netdev, ELM command state, pending command bitmap, cached CAN configuration, current CAN state, tx buffer cursor, rx fill count, and `uart_side_failure`. There is no hardware register state; persistence is the ELM327 adapter's current AT command mode and protocol configuration while attached.

Dependencies and integration points: it depends on tty line discipline APIs, SocketCAN, rx-offload manual mode, CAN bittiming constants, TTY write wakeups, workqueues, CAP_NET_ADMIN, user ioctls such as `SIOCGIFNAME`, and documented ELM327 AT command behavior. It supports listen-only control mode and a constrained bitrate set derived from divisors of 500 kbit/s.

Risks: ELM327 devices were not designed as general CAN interfaces; command echoing, prompts, buffer-full conditions, illegal characters, framing errors, and never-ending lines can force `uart_side_failure` and bus-off. Parser heuristics distinguish 11-bit and 29-bit frames by spaces and line length, so firmware formatting differences are risky. TX is serialized by stopping the netdev queue until prompts return. The driver intentionally ignores NUL chars for known PIC behavior but treats other unexpected bytes as hardware faults.

Test signals: attach/detach the line discipline, read `SIOCGIFNAME`, configure supported bitrates, netdev open/close with initialization script completion, transmit SFF/EFF/RTR frames, parse monitor output with and without echo lines, inject ELM error lines (`BUFFER FULL`, `BUS ERROR`, `CAN ERROR`, etc.), exercise partial tty writes and write wakeups, and verify illegal-character or RX-buffer-overflow paths produce bus-off and stop communication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/can327.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/can/cc770/Kconfig

Purpose: this Kconfig file defines build options for Bosch CC770 and Intel AN82527 CAN controller support and its ISA and platform bus front ends.

Important APIs, types, and functions: `CAN_CC770` is the parent tristate and depends on `HAS_IOMEM`. `CAN_CC770_ISA` enables legacy ISA support and depends on `HAS_IOPORT`. `CAN_CC770_PLATFORM` enables directly attached platform bus support.

Control flow: selecting `CAN_CC770` exposes the ISA and platform wrappers. The core `cc770.o` is built for the parent, while each wrapper is compiled only when its symbol is enabled.

State and persistence: this is build-time configuration only; it decides which CC770 objects are available.

Dependencies and integration points: it integrates with the top-level CAN Kconfig and Makefile. ISA support requires port IO capability, while platform support relies on memory-mapped device resources handled by the corresponding wrapper.

Risks: enabling the parent alone builds the core without a probing transport. ISA support can be offered only where port IO exists. Help text is generic and should stay consistent with actual subdriver coverage.

Test signals: build combinations for parent-only, ISA, platform, and both wrappers; verify `HAS_IOPORT=n` hides ISA; and confirm module dependency resolution for wrapper modules against `cc770.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/can/cc770/Makefile

Purpose: this Makefile maps CC770 Kconfig symbols to the shared core and bus-specific object files.

Important APIs, types, and functions: `obj-$(CONFIG_CAN_CC770) += cc770.o` builds the shared controller core. `obj-$(CONFIG_CAN_CC770_ISA) += cc770_isa.o` and `obj-$(CONFIG_CAN_CC770_PLATFORM) += cc770_platform.o` build the ISA and platform wrappers.

Control flow: kbuild evaluates the three symbols and compiles the corresponding objects. The wrappers depend on exported or shared core functionality from `cc770.o`.

State and persistence: the file has no runtime state; it affects build output only.

Dependencies and integration points: it must stay aligned with `cc770/Kconfig` and the source files present in the directory. The directory is entered from the top-level CAN Makefile when `CONFIG_CAN_CC770` is enabled.

Risks: stale object names or symbol mismatches break module builds. Wrapper objects built without the core would fail linkage, so Kconfig nesting and Makefile gating must remain synchronized.

Test signals: compile built-in and modular CC770 configurations, confirm expected module/object names, and run dependency checks for ISA/platform wrapper selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/Makefile -->

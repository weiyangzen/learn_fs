# subset-b-004331 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_mdio.c

## Purpose
This file is the MDIO transport binding for the Arrow SpeedChips XRS700x DSA switch family. It does not implement switch policy itself; it adapts the core XRS700x switch driver to an `mdio_device` by providing a `regmap` whose read/write callbacks translate 32-bit switch register addresses into the indirect MDIO access sequence expected by the hardware.

## Important APIs, Types, and Functions
- `xrs700x_mdio_reg_read()` and `xrs700x_mdio_reg_write()` implement the regmap bus. They split a 32-bit register into high address register `XRS_MDIO_IBA1`, low address/operation register `XRS_MDIO_IBA0`, and data register `XRS_MDIO_IBD`.
- `xrs700x_mdio_regmap_config` declares 16-bit values, 32-bit register addresses, 2-byte stride, no cache, big-endian reg/value formatting, and a max register covering `XRS_VLAN(VLAN_N_VID - 1)`.
- `xrs700x_mdio_probe()` allocates the shared XRS700x switch object via `xrs700x_switch_alloc()`, initializes devm-managed regmap, stores driver data, and calls `xrs700x_switch_register()`.
- `xrs700x_mdio_remove()` and `xrs700x_mdio_shutdown()` forward teardown/shutdown to the shared switch layer.
- `xrs700x_mdio_dt_ids` maps compatible strings for XRS7003E/F and XRS7004E/F variants to the variant info objects defined by the common driver.

## Control Flow
Probe starts when the MDIO core matches one of the OF compatible strings. The driver allocates `struct xrs700x`, creates a regmap using MDIO callbacks, stores it in device driver data, then registers the DSA switch. Register reads write the high 16 address bits to `IBA1`, write the low address bits plus `XRS_IB_READ` to `IBA0`, then read `IBD`. Register writes write the data first, then `IBA1`, then the low address plus `XRS_IB_WRITE`. Remove and shutdown are defensive and no-op when driver data has already been cleared.

## State and Persistence
Persistent runtime state is held in the common `struct xrs700x` object and in the hardware registers behind regmap. This file owns no cache because `REGCACHE_NONE` is selected. The only local state is the `mdio_device` context passed to regmap and the driver data pointer installed on probe. Shutdown clears driver data after calling the common shutdown path.

## Dependencies and Integration Points
The file depends on Linux MDIO, regmap, OF matching, DSA switch helpers from `xrs700x.h`, and register constants from `xrs700x_reg.h`. It integrates with the kernel through `mdio_module_driver()`, `MODULE_DEVICE_TABLE(of, ...)`, and the DSA registration performed by the common XRS700x switch layer.

## Risks and Edge Cases
The indirect access sequence must remain ordered; reordering the data/address writes would target the wrong register. Errors from any MDIO operation are immediately surfaced and logged. Because the regmap has no cache, every DSA operation hits hardware and depends on MDIO bus reliability. The max register is tied to VLAN table size, so new register ranges above that value would require revisiting `max_register`.

## Test Signals
Useful checks include OF probe on each compatible, regmap read/write smoke tests against known ID/revision registers, DSA registration success, VLAN register access near `VLAN_N_VID - 1`, and remove/shutdown tests that verify common switch teardown is called without stale driver data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_reg.h

## Purpose
This header defines the XRS700x hardware register address map and bit definitions consumed by the common XRS700x DSA driver and transport bindings. It is a pure register contract: base addresses, per-port address macros, control bits, counter offsets, RTC/PTP/timestamper registers, switch configuration registers, and VLAN table addressing.

## Important APIs, Types, and Functions
- Base macros such as `XRS_DEVICE_ID_BASE`, `XRS_GPIO_BASE`, `XRS_PORT_BASE(x)`, `XRS_RTC_BASE`, `XRS_TS_BASE(x)`, and `XRS_SWITCH_CONF_BASE` define the major register regions.
- Port macros cover general state, VLAN mapping, forwarding masks, HSR/PRP mode, PTP delays, counters, and inbound policy entries.
- Counter constants enumerate low/high halves for RX/TX octets, unicast, broadcast, multicast, size buckets, HSR/PRP, duplicate, and drop counters.
- RTC and timestamp macros define time, adjustment, command, per-timestamp FIFO header, and RX/TX timestamp words.
- Switch macros define global reset/configuration, MAC table, interrupt registers, timestamp tables, and `XRS_VLAN(v)` entries.

## Control Flow
There is no executable control flow. The important behavior is in address composition. Per-port blocks are built from `XRS_PORT_BASE(x)` plus section offsets, per-timestamp tables from `XRS_TS_BASE(x)`, and per-VLAN entries from `XRS_SWITCH_VLAN_BASE + 2 * vlan`. Callers use these constants to program the switch through whatever transport-specific regmap is active.

## State and Persistence
The header describes persistent hardware state. Port state, VLAN tables, MAC tables, counters, time registers, timestamp registers, and global switch configuration persist in the device until reset or reprogramming by the driver. Counter values are represented as paired 16-bit low/high registers, which places the burden for atomicity and rollover handling on the caller.

## Dependencies and Integration Points
The macros rely on kernel bit helpers such as `BIT()`. This header is included by the MDIO transport and common XRS700x implementation. It also implicitly coordinates with Linux VLAN limits because `xrs700x_mdio.c` sets regmap `max_register` using `XRS_VLAN(VLAN_N_VID - 1)`.

## Risks and Edge Cases
The register space is 16-bit value oriented with 2-byte register stride; misuse with byte offsets or incorrect port indexes will silently address the wrong hardware location. Many counter macros use `XRS_PORT_CNT_BASE(0)` rather than a port parameter, so callers must understand whether the hardware exposes a selected counter window or needs additional per-port selection. HSR/PRP, PTP, and MAC table bits are tightly encoded and require datasheet-aligned updates.

## Test Signals
Compile coverage is the first signal because misspelled macros or missing bit helpers fail quickly. Runtime signals include successful device ID reads, port state changes reflected in link behavior, VLAN table programming, monotonic counters, timestamp availability, and reset/global configuration bits behaving as expected through the common driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/yt921x.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/yt921x.c

## Purpose
This file implements a Linux DSA switch driver for Motorcomm YT921x switches, primarily YT9215-class devices and related YT9213/YT9214/YT9218 variants. It provides MDIO register transport, optional internal/external MDIO child buses, DSA switch operations, phylink MAC operations, MIB/statistics polling, bridge/VLAN/FDB/MDB/LAG/mirror/STP/MST/DCB handling, chip detection, reset, setup, and MDIO driver registration.

## Important APIs, Types, and Functions
- `yt921x_info` and `yt921x_infos[]` describe supported chip names, major IDs, mode/extmode selectors, and internal/external port masks.
- Register helpers `yt921x_reg_read/write/update_bits/wait`, 64-bit variants, and `yt921x_reg_ops_mdio` serialize accesses through `priv->reg_lock` and the MDIO-backed SMI protocol.
- `yt921x_mbus_int_*` and `yt921x_mbus_ext_*` expose switch-mediated MDIO buses for internal and external PHY access.
- MIB paths include `yt921x_mib_descs`, `yt921x_read_mib()`, `yt921x_poll_mib()`, and DSA ethtool/stat callbacks.
- Switch offload callbacks include EEE, MTU, mirror, LAG, FDB/MDB, VLAN, bridge, STP/MST, optional DCB app/default-priority and DSCP priority hooks.
- Phylink hooks `yt921x_phylink_mac_config/link_up/link_down` configure external SERDES and force port status.
- Chip lifecycle functions `yt921x_chip_detect()`, `yt921x_chip_reset()`, `yt921x_chip_setup_dsa()`, `yt921x_chip_setup()`, and `yt921x_dsa_setup()` establish the hardware mode.
- `yt921x_mdio_probe/remove/shutdown` bind the DSA switch to the MDIO core.

## Control Flow
Probe allocates `yt921x_priv` and MDIO context, initializes `reg_lock`, delayed MIB work per port, DSA metadata, phylink ops, lag limits, ageing limits, and registers the DSA switch. DSA setup resets and detects the chip under the register lock, optionally registers an internal `mdio` child bus, refuses the currently untested external bus path, then enables MIBs, DSA CPU tagging/copy/trap behavior, VLAN 0 handling, QoS defaults when DCB is enabled, clears MIB counters, and enables the temperature sensor.

Register reads and writes are four-step MDIO SMI operations with a bus-level nested MDIO lock. For MDIO child buses, the driver waits for the internal or external management bus, programs port/reg/type/op control fields, starts the operation, waits again, and reads or writes data.

The DSA data path is configured by callbacks. Port setup starts ports in standalone mode, disables learning, traps user traffic to CPU by isolation, and gives CPU ports special one-way isolation. Bridge joins clear learning disable and recompute per-port isolation masks; bridge leave restores standalone isolation. VLAN operations program 64-bit VLAN table entries and per-port PVID/drop/TPID settings. FDB/MDB operations share the hardware FDB engine, using get-one, get-next, add, delete, and flush operations. Phylink config selects SERDES modes for external ports, while link up writes port/serdes/mdio-polling speed, duplex, pause, and link bits.

## State and Persistence
Driver state lives in `struct yt921x_priv`: DSA switch object, chip info, cached CPU-port mask, register lock, register transport, optional MDIO buses, per-port structures, and an EEE port mask. Per-port state includes index, bridge hairpin/isolated flags, delayed MIB work, accumulated MIB values, and derived RX/TX frame totals. Hardware state includes FDB, VLAN table, STP/MST state, isolation masks, LAG tables, QoS maps, MIB counters, EEE, port MAC/SERDES state, and CPU tagging configuration. MIB values are polled and accumulated to handle 32-bit wrap; reads are intentionally not made globally consistent because hardware has no snapshot facility.

## Dependencies and Integration Points
The driver integrates with Linux DSA (`struct dsa_switch_ops`), phylink, MDIO/OF MDIO, bridge and switchdev objects, ethtool stats, DCB when enabled, DSCP/802.1Q helpers, and the YT921x tag protocol (`DSA_TAG_PROTO_YT921X`). It depends heavily on register definitions from `yt921x.h`. Device tree matching currently exposes `motorcomm,yt9215`.

## Risks and Edge Cases
The code contains several explicit uncertainty markers: only YT9215+SGMII is stated as tested, external MDIO registration returns `-ENODEV`, XMII support is declared as not tested, and several MBUS bit fields are marked as guesses. The FDB walk must never issue GET_NEXT with index 4095 because the hardware can hang until reset. Port isolation is used to emulate DSA bridge membership because native hardware bridging is insufficient for multiple bridge domains; unknown unicast/multicast traffic is trapped rather than dropped to preserve correctness. Register writes require `reg_lock`; missing the lock trips `WARN_ON` but would also risk interleaving SMI transactions. VLAN entries must be written as 64-bit values. MIB polling is delayed-work based and may return transiently inconsistent counters.

## Test Signals
High-value signals include successful probe and chip detection for each claimed mode/extmode, CPU tag EtherType verification, DSA setup with internal PHY MDIO child nodes, link-up/link-down for internal and SGMII/1000BASE-X/2500BASE-X external ports, bridge isolation tests across multiple bridges, VLAN add/delete/PVID/filtering tests, FDB/MDB add/delete/dump/fast-age tests including multicast entries, LAG membership/hash validation, ethtool MIB wrap behavior, EEE toggling, STP/MST transitions, DCB app trust/DSCP mapping when enabled, and shutdown/remove cancellation of all delayed MIB work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/yt921x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/yt921x.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/yt921x.h

## Purpose
This header is the hardware and driver state contract for the Motorcomm YT921x DSA driver. It defines SMI/MDIO framing, register offsets, bit fields, constants, MIB layout, port predicates, and private driver structures shared by `yt921x.c`.

## Important APIs, Types, and Functions
- SMI macros define switch ID selection, address/data phases, and read/write phases.
- Register definitions cover reset/function/chip ID, CPU tag configuration, PVID selection, SERDES/XMII, port control/status, MIB, embedded data, internal/external MBUS, egress/ingress TPID, priority maps, VLAN filtering, STP/MST, learning, FDB, flood/trap actions, VLAN table, LAG hashing/membership, and mirroring.
- Constants define table and hardware limits: `YT921X_FDB_NUM`, `YT921X_MSTI_NUM`, `YT921X_LAG_NUM`, `YT921X_LAG_PORT_NUM`, `YT921X_PRIO_NUM`, `YT921X_FRAME_SIZE_MAX`, `YT921X_TAG_LEN`, and `YT921X_PORT_NUM`.
- `struct yt921x_mib` mirrors the MIB descriptor table in `yt921x.c`.
- `struct yt921x_port`, `struct yt921x_reg_ops`, and `struct yt921x_priv` define per-port and whole-switch runtime state.

## Control Flow
The header has no executable control flow. Its macros are used by the C file to compose register operations. Examples include per-port address calculation (`YT921X_PORTn_CTRL(port)`), per-VLAN 64-bit table entries (`YT921X_VLANn_CTRL(vlan)`), bit-field construction with `FIELD_PREP`, and port classification with `yt921x_port_is_internal()` / `yt921x_port_is_external()`.

## State and Persistence
The hardware state described here is persistent until changed by driver writes or reset: FDB entries, VLAN rows, LAG membership, QoS maps, isolation masks, port status, SERDES/XMII settings, MIB counters, EEE settings, CPU tag TPID, and chip strap/mode data. The driver state structs persist in memory for the MDIO device lifetime and include locks, DSA integration state, MDIO child bus pointers, delayed MIB work, cached counters, and EEE mask.

## Dependencies and Integration Points
The header includes `<net/dsa.h>` and assumes kernel bitfield helpers are available to the including C file. It is tightly coupled to `yt921x.c`: the order of `struct yt921x_mib` fields must match `yt921x_mib_descs[]`, and register definitions must match the control flow in FDB, VLAN, MIB, phylink, and DSA setup code.

## Risks and Edge Cases
Some comments mark fields as guesses or untested, especially MBUS type/op encodings and broader external/XMII support. `yt921x_port_is_external(port)` currently treats only port 8 as external even though comments and masks mention two external ports, so code using that predicate needs scrutiny for port 9 support. Many bit macros accept a port or index without bounds checks; callers must enforce hardware limits. The FDB and VLAN macros encode wide fields where incorrect use of non-64-bit helpers would lose upper bits.

## Test Signals
Compile-time coverage catches missing macros and structure mismatches. Runtime validation should compare known chip ID/mode detection, port status bits, VLAN table membership, FDB operations, MIB counter offsets, LAG hash fields, and SERDES/XMII mode writes against hardware behavior and datasheet traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/yt921x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dummy.c -->
# sources/distributed-fs/ceph-client/drivers/net/dummy.c

## Purpose
This file implements the kernel dummy network device driver. A dummy netdev accepts transmitted packets, accounts them, timestamps them, and drops them. It provides a stable addressable network interface for routing, testing, namespace setup, and configurations that need an interface without real packet transmission.

## Important APIs, Types, and Functions
- `dummy_xmit()` is the transmit path: it updates per-CPU lightweight TX stats with `dev_lstats_add()`, applies `skb_tx_timestamp()`, frees the skb, and returns `NETDEV_TX_OK`.
- `dummy_get_stats64()` reads lightweight TX packet/byte counters through `dev_lstats_read()`.
- `dummy_dev_init()` selects `NETDEV_PCPU_STAT_LSTATS` and installs lockdep classes.
- `dummy_change_carrier()` lets userspace toggle carrier state.
- `dummy_setup()` configures Ethernet defaults, no ARP, no multicast flag, no queue, live address changes, checksum/GSO/highdma feature masks, random MAC, and zero min/max MTU.
- `dummy_validate()` validates an optional netlink MAC address.
- `dummy_link_ops` registers rtnetlink kind `dummy`.

## Control Flow
Module init registers the rtnetlink link kind, then under the init net namespace lock creates `numdummies` default devices named `dummy%d`. Each device is allocated with `alloc_netdev()` and `dummy_setup()`, associated with `dummy_link_ops`, and registered. Additional devices can be created through rtnetlink. Transmit calls never leave the host: the skb is accounted, timestamped, and freed. Module exit unregisters the link kind, which tears down devices through netdev core ownership.

## State and Persistence
State is mostly netdev core state: per-CPU lightweight TX stats, carrier state, MAC address, flags, feature masks, and rtnetlink-created device instances. The module parameter `numdummies` controls initial device count at load time. Devices use `needs_free_netdev = true`, so the netdev core owns freeing after unregister.

## Dependencies and Integration Points
The driver integrates with rtnetlink (`rtnl_link_ops`), Ethernet helpers (`ether_setup`, address validation/change helpers), ethtool timestamp info, netdev per-CPU lightweight stats, and skb timestamping. It advertises `MODULE_ALIAS_RTNL_LINK("dummy")` for autoloading by link kind.

## Risks and Edge Cases
Because transmit always succeeds and drops, dummy devices can hide routing or policy mistakes during testing. `min_mtu` and `max_mtu` are both zero, preserving dummy semantics but differing from physical Ethernet devices. The multicast setter is intentionally empty while multicast is disabled in flags. Initial device creation is only in `init_net`; per-netns devices are handled through rtnetlink creation.

## Test Signals
Tests should cover module load with different `numdummies`, `ip link add type dummy`, MAC validation, carrier toggling, TX packet/byte counter increments after ping or packet injection, timestamp info via ethtool, feature visibility, MTU behavior, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/eql.c -->
# sources/distributed-fs/ceph-client/drivers/net/eql.c

## Purpose
This file implements the legacy Equalizer load-balancer for serial network interfaces. It exposes one master netdev named `eql` and allows privileged userspace private ioctls to enslave or remove serial-like slave devices. Transmit scheduling selects the currently least-loaded live slave and forwards the skb to that device.

## Important APIs, Types, and Functions
- `eql_setup()` initializes `equalizer_t`, its timer, slave queue lock/list, netdev ops, master flags, SLIP ARP type, MTU, and short TX queue length.
- `eql_open()` initializes min/max slave counts and starts the periodic timer.
- `eql_timer()` periodically decays each slave's `bytes_queued` by `priority_Bps` or removes down slaves.
- `__eql_schedule_slaves()` picks the live slave with the lowest load metric based on queued bytes and priority.
- `eql_slave_xmit()` forwards skb transmission through the selected slave with `dev_queue_xmit()`, or drops when no slave is available.
- Private ioctl handlers implement enslave, emancipate, get/set slave config, and get/set master config using `if_eql.h` request structs.
- `eql_kill_one_slave()` and `eql_kill_slave_queue()` remove references, clear `IFF_SLAVE`, and free slave records.

## Control Flow
Module init allocates and registers the `eql` netdev. Opening the master starts a timer and requires an empty slave list. Userspace adds slaves through `EQL_ENSLAVE`, which validates privileges, copies the request, looks up the target in `init_net`, checks that it is neither master nor already slave, allocates a `slave_t`, and inserts it under the queue spinlock. Transmit locks the queue, schedules the best slave, rewrites `skb->dev`, marks filler priority, increments that slave's queued-byte estimate, and sends via `dev_queue_xmit()`. The timer keeps the load metric from growing forever and cleans down slaves. Closing deletes the timer synchronously and removes all slaves.

## State and Persistence
The master private state is `equalizer_t`, including a timer, min/max slave configuration, and a `slave_queue_t` list. Each `slave_t` stores a held netdev reference, priority in bits/sec and bytes/sec, queued-byte estimate, and list node. State exists only while the module and `eql` netdev are loaded; configuration is runtime-only through private ioctls. Slave ownership is marked in `dev->flags` with `IFF_SLAVE`.

## Dependencies and Integration Points
The driver depends on legacy `linux/if_eql.h` ABI structs and commands, netdevice core, timers, spinlocks, `dev_queue_xmit()`, rtnet stats, `CAP_NET_ADMIN`, and user-copy helpers. It operates in `init_net` for slave lookup and does not implement compat ioctl translation.

## Risks and Edge Cases
The driver is legacy and lacks modern bonding/team semantics. Compat syscalls return `-EOPNOTSUPP`. It mutates device `IFF_SLAVE` flags directly and rejects devices already marked master/slave. Transmit holds the queue spinlock while calling `dev_queue_xmit()`, which is a historical design worth scrutinizing for modern locking expectations. The load metric is approximate, timer-based, and can be skewed by priority configuration. Down slave cleanup happens opportunistically during timer and scheduling passes.

## Test Signals
Tests should cover module load creating `eql`, private ioctl permission checks, enslave/emancipate flows, duplicate slave replacement, max slave enforcement, priority updates, transmit distribution across different priorities, down-slave removal, close cleanup releasing netdev references, and compat ioctl rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/eql.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/3c59x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/3c59x.c

## Purpose
This file is the legacy 3Com 3c59x/3c9xx Ethernet driver for Vortex, Boomerang, Cyclone, Tornado, Hurricane, and related PCI/CardBus/EISA adapters. It supports both older programmed-I/O FIFO devices and newer bus-master descriptor-ring devices, media selection, MII management, ethtool, Wake-on-LAN, VLAN frame handling, power management, and PCI/EISA registration.

## Important APIs, Types, and Functions
- Hardware identification is driven by `vortex_chip_info`, `vortex_pci_tbl`, and EISA IDs. Flags distinguish Vortex/Boomerang/Cyclone/Tornado, MII/NWay, checksum, EEPROM quirks, power quirks, and reset quirks.
- Register definitions cover command/status, windows 0/1/2/3/4/7, EEPROM, media bits, bus-master registers, RX/TX descriptors, and status fields.
- `struct vortex_private` holds descriptor rings, skb arrays, DMA addresses, I/O mappings, media state, MII info, timers, stats, options, locks, and chip flags.
- Probe paths `vortex_init_one()`, `vortex_eisa_probe()`, and `vortex_probe1()` enable resources, map I/O, read EEPROM, choose media/features, allocate coherent rings, register netdevs, and set PM/WOL state.
- Runtime paths include `vortex_open()`, `vortex_up()`, `vortex_start_xmit()`, `boomerang_start_xmit()`, `_vortex_interrupt()`, `_boomerang_interrupt()`, `vortex_rx()`, `boomerang_rx()`, `vortex_down()`, and `vortex_close()`.
- Management paths include `vortex_timer()`, `vortex_check_media()`, MDIO bit-bang read/write, ethtool callbacks, MII ioctl, stats update, RX filter setting, VLAN mode, WOL, suspend/resume, and remove/cleanup.

## Control Flow
PCI probe enables the device, requests regions, selects MMIO or I/O BAR, maps it, then calls common probe. Common probe allocates an Ethernet device, applies module options, sets PCI latency for Vortex quirks, initializes locks/MII, allocates coherent RX/TX rings, reads EEPROM and MAC address, discovers MII PHYs, selects full-bus-master or FIFO netdev ops, enables checksum/scatter-gather when available, saves PCI state, configures WOL, and registers the netdev.

Open requests the shared IRQ, fills the RX ring for bus-master devices, then calls `vortex_up()`. Bring-up powers the device, restores PCI state, selects media, starts the media timer, configures duplex, resets TX/RX, programs station address, media bits, stats, RX/TX rings, RX filter, VLAN mode, enables stats/RX/TX, enables interrupts, and starts the queue.

TX uses two paths. `vortex_start_xmit()` writes packet length/data to the FIFO, optionally using the single bus-master controller for a contiguous DMA transfer. `boomerang_start_xmit()` fills descriptor-ring entries, maps skb head/frags for DMA, links the descriptor under `vp->lock`, starts or unstalls the download engine, manages queue stop/wake thresholds, and relies on `DownComplete` interrupts to free skbs. RX similarly splits: `vortex_rx()` drains FIFO packets and pushes allocated skbs, while `boomerang_rx()` consumes completed RX descriptors, either copies small packets below `rx_copybreak` or swaps in replacement buffers for larger packets, handles checksum status, and returns buffers to hardware.

Interrupt dispatch takes `vp->lock` and calls either Vortex or Boomerang handlers. Handlers loop up to `max_interrupt_work`, process RX, TX completion/availability, DMA done, stats, host errors, and deferred interrupts. Error handling can reset TX/RX paths or fully reset and reinitialize on severe PCI bus errors. Close/down disables queues, timer, stats, RX/TX, VLAN mode, interrupts, WOL/PM state, IRQ, and DMA buffers.

## State and Persistence
Driver state persists in `struct vortex_private` for each netdev: descriptor rings and DMA addresses, queued skbs, ring cursors, media options, MII PHY address, WOL flag, cached EEPROM-derived capabilities, stats, and synchronization locks. Hardware state includes EEPROM configuration, windowed registers, media transceiver selection, MAC address registers, RX filter, descriptor list pointers, stats counters, MII PHY state, and PCI power state. Module parameters persist for the module lifetime and influence per-card options, full duplex, checksum, flow control, WOL, MMIO choice, debug level, RX copybreak, interrupt work limit, watchdog, and Compaq workaround addresses.

## Dependencies and Integration Points
The file integrates with PCI, EISA, netdevice ops, DMA mapping, IRQ handling, MII library, ethtool, VLAN 802.1Q support, PCI PM, WOL, netpoll, and legacy module parameters. It uses MMIO/PIO accessors and software MDIO bit-banging through the card's physical management register.

## Risks and Edge Cases
This is hardware-quirk-heavy code. EEPROM formats differ by chip; invalid all-zero MACs are rejected. Older Vortex chips need PCI latency adjustment. CardBus power bits can be inverted. MII preamble requirements are global rather than per-device. The code supports hot-unplug-like status `0xffff`, shared IRQs, interrupt work deferral, and a Compaq BIOS workaround path with no `struct device`. Descriptor DMA error paths must avoid leaking mappings. Some comments mark known issues, including host-error reinit assuming a full RX ring and interrupt mitigation concerns. Lock ordering is documented as RTNL above private locks above window lock; violating it risks deadlock.

## Test Signals
Valuable tests include PCI ID probe across representative Vortex and Boomerang/Cyclone/Tornado devices, EEPROM MAC/checksum handling, MII PHY discovery and ethtool link settings, open/close with IRQ and DMA allocation, FIFO TX/RX on Vortex, descriptor TX/RX with fragmented skbs and checksum offload on Boomerang-class hardware, RX copybreak behavior, VLAN tagged frame reception, multicast/promiscuous filter changes, media autoselection and timeout failover, TX timeout recovery, stats/ethtool counters, WOL set/get and suspend/resume, EISA probe/remove when configured, and cleanup without DMA or IRQ leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/3c59x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/Kconfig

## Purpose
This Kconfig file exposes configuration options for 3Com Ethernet device drivers. It gates the 3Com vendor menu and defines build-time options for the Vortex/Boomerang family driver and the Typhoon 3CR990-family driver.

## Important APIs, Types, and Functions
- `NET_VENDOR_3COM` is a boolean vendor menu option defaulting to `y` when ISA, EISA, PCI, or PCMCIA support exists.
- `VORTEX` is a tristate for `3c59x.c`, depends on `(PCI || EISA) && HAS_IOPORT_MAP`, and selects `MII`.
- `TYPHOON` is a tristate for the Typhoon driver, depends on PCI, and selects `CRC32`.

## Control Flow
Kconfig evaluation first asks whether 3Com devices should be shown. If enabled, it presents individual driver choices. Enabling `VORTEX` builds in or modules the 3c590/3c900-series support and ensures the MII library is available. Enabling `TYPHOON` does the same for 3CR990 devices with CRC32 support.

## State and Persistence
The persistent output is kernel configuration state: `CONFIG_NET_VENDOR_3COM`, `CONFIG_VORTEX`, and `CONFIG_TYPHOON`. These symbols drive Makefile object inclusion and preprocessor conditionals in driver code.

## Dependencies and Integration Points
This file integrates with `drivers/net/ethernet/3com/Makefile`, where `CONFIG_VORTEX` selects `3c59x.o` and `CONFIG_TYPHOON` selects `typhoon.o`. Help text points users to the Vortex documentation and source comments for supported cards.

## Risks and Edge Cases
If `NET_VENDOR_3COM` is disabled, specific 3Com drivers are hidden even though no kernel behavior changes directly from the vendor symbol itself. `VORTEX` requires `HAS_IOPORT_MAP`, which matters for EISA and I/O-port paths. The help text lists broad families and expects users to match old product names accurately.

## Test Signals
Configuration tests should verify menu visibility under ISA/EISA/PCI/PCMCIA combinations, dependency enforcement for `HAS_IOPORT_MAP`, automatic `MII` selection for `VORTEX`, automatic `CRC32` selection for `TYPHOON`, and Makefile object inclusion for built-in and module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/Makefile

## Purpose
This Makefile maps 3Com Ethernet Kconfig symbols to build objects. It is the build glue for the 3Com Ethernet driver directory.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_VORTEX) += 3c59x.o` builds the Vortex/Boomerang/Cyclone/Tornado driver when selected.
- `obj-$(CONFIG_TYPHOON) += typhoon.o` builds the Typhoon 3CR990-family driver when selected.

## Control Flow
Kbuild expands the `obj-y` or `obj-m` lists depending on each symbol's tristate value. Built-in selections compile into the kernel image; module selections produce loadable modules.

## State and Persistence
There is no runtime state. The persistent effect is build output determined by `.config`.

## Dependencies and Integration Points
The file depends on symbols defined in the neighboring Kconfig. It integrates with the kernel top-level Kbuild recursion for `drivers/net/ethernet/3com`.

## Risks and Edge Cases
The file is intentionally minimal; mismatches between Kconfig symbol names and object names would silently omit drivers from builds. Any new 3Com driver added to Kconfig must also be listed here.

## Test Signals
Build tests should check `CONFIG_VORTEX=y/m` and `CONFIG_TYPHOON=y/m` produce the expected built-in objects or modules, and that disabling them omits the objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/3com/Makefile -->

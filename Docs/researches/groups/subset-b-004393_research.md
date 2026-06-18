# subset-b-004393 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cxgb2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cxgb2.c

## Purpose
`cxgb2.c` is the PCI and Linux netdevice front end for the Chelsio T1/T2 `cxgb` Ethernet driver. It binds supported PCI IDs, allocates one shared `struct adapter` plus one netdevice per physical port, wires netdevice and ethtool operations, starts and stops the shared DMA/interrupt hardware, and bridges link/MAC/PHY/SGE/TP/ESPI helpers into normal kernel networking operations.

## Important APIs, Types, and Functions
The key external entry points are the PCI driver's `init_one()` and `remove_one()`, exported through `module_pci_driver(cxgb_pci_driver)`. Netdevice operations are collected in `cxgb_netdev_ops`, with `cxgb_open()`, `cxgb_close()`, `t1_start_xmit()` from `sge.c`, `t1_get_stats()`, MTU/MAC/rx-mode setters, MII ioctl support, and feature negotiation. `t1_ethtool_ops` exposes driver info, register dumps, ring sizing, coalescing, EEPROM reads, link settings, pause parameters, and statistics.

Important internal helpers include `cxgb_up()` and `cxgb_down()` for card-wide hardware activation, `link_start()` and `t1_link_negotiated()` for MAC/PHY link transitions, `enable_hw_csum()` for TP checksum offload, `mac_stats_task()` for periodic MAC counter accumulation, and `t1_clock()`/`bit_bang()` for T1B clock programming through Elmer0 GPIO.

## Control Flow
Probe enables the PCI function, verifies BAR0 memory, sets a 64-bit DMA mask, requests regions, maps MMIO, determines board revision, initializes locks/work, allocates per-port netdevices, assigns features and ethtool/netdev ops, creates software modules through `t1_init_sw_modules()`, and registers each port. Open enables NAPI, performs first-use hardware initialization through `t1_init_hw_modules()`, requests a threaded IRQ, starts SGE, enables interrupts, starts the port MAC/PHY, and schedules MAC stats. Close stops the queue, disables NAPI and MAC directions, clears the port from `open_device_map`, cancels stats once all ports are down, and tears down SGE/IRQ/MSI when no port remains open. Remove unregisters registered netdevices, frees modules, unmaps MMIO, frees netdevices, releases PCI resources, disables the device, and performs a software reset through PCI config space.

## State and Persistence
State is runtime-only kernel driver state. `adapter->flags` tracks full hardware initialization, `open_device_map` tracks active ports, `registered_device_map` tracks successfully registered netdevices, `params` carries board/chip/SGE/PCI configuration, and `msg_enable` stores ethtool message level. Per-port link state lives in `struct port_info` and `struct link_config`; netdevice stats are recomputed from MAC counters. Module parameters `dflt_msg_enable`, `t1powersave`, and `disable_msi` influence runtime behavior but are not persisted by this file.

## Dependencies and Integration Points
This file depends on the Linux PCI, netdevice, ethtool, NAPI, IRQ, DMA, VLAN, MII, and workqueue APIs. Driver-internal dependencies include `common.h` for adapter/board state, `regs.h` register constants, `gmac.h` MAC operations, `cphy.h` PHY operations, `sge.h` DMA/interrupt/TX/RX, `tp.h` checksum offload, `espi.h` ESPI counters, and `elmer0.h` GPIO/TPI addresses. It integrates with `subr.c` for board discovery/module initialization/slow interrupt handling and with the MAC/PHY/SGE modules researched in this group.

## Risks
The main risks are shared-card lifecycle races across multiple netdevices, especially NAPI enable/disable and card-wide IRQ/SGE ownership while only some ports are open. Error unwinding in `init_one()` must free partially allocated per-port devices without leaking the first netdevice that embeds the adapter. Ettool ring sizing is rejected after `FULL_INIT_DONE`, so runtime resizing assumptions can fail. `t1_clock()` performs timing-sensitive GPIO serial programming under `tpi_lock`; interrupted or wrong-mode use can misprogram clocks. EEPROM read offsets rely on a small local buffer and must stay bounded by ethtool's length checks.

## Test Signals
Useful signals include PCI probe/remove, module load/unload, multi-port open/close permutations, MSI and shared-IRQ operation, NAPI traffic, link up/down reporting, ethtool stats/register/eeprom/ring/coalesce/link/pause operations, MTU and MAC address changes, VLAN feature toggles, netpoll if enabled, T1B power-save clock mode coverage, and fault-injection of probe failures after each allocation stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cxgb2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/elmer0.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/elmer0.h

## Purpose
`elmer0.h` defines the register offsets and bitfields for the Elmer0 FPGA/bridge used by Chelsio T1/T2 adapters. It is a pure hardware contract header: code uses these constants to access board-version, PHY configuration, external interrupt, GPIO, and MI1 MDIO-management registers through TPI accesses.

## Important APIs, Types, and Functions
The file exports no functions. It defines Elmer0 flavor IDs, top-level registers such as `A_ELMER0_VERSION`, `A_ELMER0_PHY_CFG`, `A_ELMER0_INT_ENABLE`, `A_ELMER0_INT_CAUSE`, `A_ELMER0_GPI_CFG`, `A_ELMER0_GPI_STAT`, `A_ELMER0_GPO`, and per-port MI1 register groups from port 0 through port 3. It also defines standard Chelsio `S_`, `M_`, `V_`, `G_`, and `F_` bitfield helpers for MI1 configuration, register/PHY addressing, data, operation selection, address auto-increment, and busy state.

The GPIO bit constants `ELMER0_GP_BIT0` through `ELMER0_GP_BIT19` are used by PHY/MAC drivers to reset external chips, enable lasers, toggle activity LEDs, and route external interrupts. `MI1_OP_DIRECT_WRITE`, `MI1_OP_DIRECT_READ`, and indirect operation constants define MDIO command encodings.

## Control Flow
There is no executable control flow. Runtime users compose Elmer0 register addresses and bitfields, then call `t1_tpi_read()`, `t1_tpi_write()`, `__t1_tpi_read()`, or `__t1_tpi_write()` to reach the FPGA. Interrupt-enable paths set bits in `A_ELMER0_INT_ENABLE`; clear paths write `A_ELMER0_INT_CAUSE`; reset/LED/clock paths manipulate `A_ELMER0_GPO`; MDIO paths use per-port MI1 config/address/data/op registers and poll `F_MI1_OP_BUSY`.

## State and Persistence
The header defines access to board hardware state but owns no memory. The persistent state is the Elmer0 register contents in the adapter until reset or power cycle: GPIO output level, interrupt masks/causes, and MI1 configuration. Some PHY code caches selected GPIO state in `struct cphy`, but this header only defines the bits.

## Dependencies and Integration Points
`cxgb2.c` uses `A_ELMER0_GPO` for T1B clock programming. `mv88e1xxx.c`, `mv88x201x.c`, `my3126.c`, and `pm3393.c` use Elmer0 GPIO and interrupt registers for PHY/MAC reset, external interrupt routing, LED/laser control, and clearing interrupt causes. The MDIO/TPI helpers in other driver files rely on the MI1 field definitions here.

## Risks
Because these constants map physical hardware registers, incorrect offsets or bit positions can reset the wrong external chip, leave interrupts stuck, or break MDIO access. GPIO bits are reused for board-specific semantics, so callers must combine this header with board type checks. Busy-bit polling and interrupt cause semantics are easy to misuse because the header does not encode timing requirements or write-one-to-clear behavior.

## Test Signals
Signals include successful PHY MDIO reads/writes on all ports, external interrupt enable/disable/clear behavior, link interrupt delivery from Marvell PHYs, PM3393 reset through GPIO bit 0, 10G PHY reset/laser enable through GPIO bits used by `mv88x201x` and `my3126`, T1B clock switching through `cxgb2.c`, and no stuck Elmer0 interrupt causes after link flaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/elmer0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/espi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/espi.c

## Purpose
`espi.c` implements Ethernet SPI4/ESPI initialization, interrupt accounting, and monitor-counter access for Chelsio T1/T2 adapters. It programs ESPI calendars, FIFO watermarks, burst sizes, training, port counts, and T2 TRICN settings according to the attached MAC type and number of ports.

## Important APIs, Types, and Functions
The private `struct peespi` stores the adapter pointer, `struct espi_intr_counts`, a shadow `misc_ctrl`, and a lock for monitored-counter selection. Public APIs are `t1_espi_create()`, `t1_espi_destroy()`, `t1_espi_init()`, `t1_espi_intr_enable()`, `t1_espi_intr_disable()`, `t1_espi_intr_clear()`, `t1_espi_intr_handler()`, `t1_espi_get_intr_counts()`, `t1_espi_get_mon()`, and `t1_espi_get_mon_t204()`.

Key private helpers include `tricn_write()` and `tricn_init()` for T2 TRICN register programming, plus `espi_setup_for_pm3393()`, `espi_setup_for_vsc7321()`, and `espi_setup_for_ixf1010()` for MAC-specific ESPI setup.

## Control Flow
Creation allocates and binds a `peespi` to an adapter. `t1_espi_init()` disables training by default, programs T2 or T1 burst/misc thresholds, dispatches to a MAC-specific setup routine, enables RX FIFO status, and for T2 initializes TRICN plus monitor-counter selection. Interrupt enable masks ESPI drops/parity/DIP errors except on T1B where a documented hardware bug prevents reliable clearing. The interrupt handler reads `A_ESPI_INTR_STATUS`, increments software counters for each asserted cause, reads the DIP2 error count when needed to clear that source, writes back the appropriate status value, and returns.

Monitor reads use `A_ESPI_MISC_CONTROL` to select the requested port/direction/interface and read `A_ESPI_SCH_TOKEN3`. `t1_espi_get_mon()` supports single-port monitored counters with optional trylock behavior; `t1_espi_get_mon_t204()` reads all T204 ingress TX SOP counters while preserving the shadow control value.

## State and Persistence
Persistent hardware state includes ESPI FIFO thresholds, calendar length, port count, training/burst settings, interrupt enable bits, and misc monitor selection. Software state is limited to accumulated interrupt counters and `misc_ctrl`. No data survives driver unload or hardware reset.

## Dependencies and Integration Points
The file depends on `common.h`, `regs.h`, and `espi.h`. It is called during hardware initialization from the common module setup path and observed by `cxgb2.c` ethtool statistics through `t1_espi_get_intr_counts()`. `sge.c` uses `t1_espi_get_mon()` and `t1_espi_get_mon_t204()` for the T2 stuck-packet workaround. Interrupt control integrates with the PL interrupt registers `A_PL_ENABLE` and `A_PL_CAUSE`.

## Risks
Risks are hardware-revision sensitive. Enabling ESPI interrupts on T1B can create unclearable interrupts, so the mask must remain conditional. Wrong MAC type or port count programming can break SPI4 framing or FIFO scheduling. Monitor-counter reads temporarily rewrite `A_ESPI_MISC_CONTROL`; missing locking would corrupt concurrent workaround reads. TRICN writes poll only a bounded number of attempts, so timeout handling is limited to error logging and a busy return.

## Test Signals
Test signals include successful adapter initialization for PM3393, VSC7321, and IXF1010 boards; correct interrupt counters under induced DIP/drop/parity events; no ESPI interrupt storm on T1B; T2 TRICN initialization only after RX clock-ready; stable `ethtool -S` ESPI counters; and T204 stuck-packet workaround monitor reads that do not race or leave `A_ESPI_MISC_CONTROL` misselected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/espi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/espi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/espi.h

## Purpose
`espi.h` is the public interface for the cxgb ESPI module. It exposes the opaque `struct peespi` handle, ESPI interrupt counter shape, lifecycle functions, interrupt controls, and monitor-counter accessors used by the adapter, ethtool, and SGE workaround code.

## Important APIs, Types, and Functions
`struct espi_intr_counts` contains six software counters: DIP4 errors, RX drops, TX drops, RX overflow, RAM parity errors, and DIP2 parity errors. `struct peespi` is forward-declared to keep implementation state private. The lifecycle API is `t1_espi_create()`, `t1_espi_destroy()`, and `t1_espi_init()`. Interrupt APIs are `t1_espi_intr_enable()`, `t1_espi_intr_clear()`, `t1_espi_intr_disable()`, `t1_espi_intr_handler()`, and `t1_espi_get_intr_counts()`. Monitor APIs are `t1_espi_get_mon()` and `t1_espi_get_mon_t204()`.

## Control Flow
The typical flow is: create the ESPI object during software module setup, initialize it during hardware bring-up with MAC type and port count, enable/clear/disable interrupts as part of adapter-wide interrupt control, call the handler from the slow interrupt path when PL reports ESPI activity, and expose the accumulated counters through ethtool. T2-specific timers in `sge.c` may call the monitor accessors while the adapter is running.

## State and Persistence
The header itself has no state. It defines access to `espi.c` state: a heap-allocated ESPI object tied to an adapter and a set of monotonically increasing software interrupt counters. State is runtime-only and is freed on module teardown.

## Dependencies and Integration Points
It includes `common.h` for `adapter_t` and kernel integer types. `cxgb2.c` uses the counter getter for ethtool statistics. `subr.c` and adapter interrupt code call the interrupt functions. `sge.c` calls monitor functions for T2 ESPI stuck-packet workarounds.

## Risks
Since `struct peespi` is opaque, callers must respect lifecycle ordering and not call interrupt or monitor operations before create/init or after destroy. The monitor APIs expose a `wait` argument; using non-waiting mode requires handling a zero or negative return as lock contention rather than a meaningful counter. Counter fields are plain unsigned integers and can wrap on long-running systems.

## Test Signals
Signals include successful build of all users after prototype changes, adapter initialization with an ESPI object, ethtool ESPI stats matching handler increments, slow interrupt dispatch invoking `t1_espi_intr_handler()`, and SGE workaround timers receiving valid monitor values on T2/T204 without deadlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/espi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/fpga_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/fpga_defs.h

## Purpose
`fpga_defs.h` defines register offsets and bitfields for FPGA-based Chelsio cxgb hardware paths, including FPGA-level interrupt routing, TP/MC3/GMAC interrupt registers, MI0 MDIO access, and a compact GMAC register map. It is a hardware definition header, not executable code.

## Important APIs, Types, and Functions
The file exports no functions or structures. Important constants include FPGA PCIX version/status addresses and master interrupt bits for SGE, TP, MC3, GMAC, and PCIX; TP interrupt cause/enable addresses; MC3 and GMAC interrupt address groups; MI0 clock/CSR/address/data registers and bitfield helpers; GMAC station address, control, inter-frame spacing, jumbo length, link delay, pause, multicast filter, random backoff, and TX FIFO threshold registers. `MAC_REG_ADDR(idx, reg)` and derived `MAC_REG_*` macros compute per-port GMAC register offsets.

## Control Flow
There is no direct control flow. Runtime code uses these constants to configure FPGA variants, access MI0 MDIO state, manipulate GMAC control bits, and service FPGA interrupt causes. The macros follow the same shift/mask/value/getter convention as `regs.h`, so callers assemble register values with `V_*` and test fields with `G_*`/`F_*`.

## State and Persistence
All state represented by this file is hardware state in FPGA registers: interrupt masks/causes, MI0 operation status, GMAC enable/loopback/speed/pause/promiscuous/multicast/jumbo settings, and per-port MAC address/filter registers. The header owns no driver memory and persists nothing outside the device.

## Dependencies and Integration Points
This header is a legacy FPGA companion to the ASIC register map in `regs.h`. It integrates with lower-level board initialization, MDIO, and GMAC code that must support FPGA hardware revisions. The constants overlap conceptually with `gmac.h` operation callbacks but sit at the register-access layer.

## Risks
Risk is primarily register-map drift or mixing FPGA and ASIC paths. Applying these offsets to an ASIC BAR or using ASIC constants against an FPGA target could corrupt unrelated registers. The generic macro names for GMAC control bits also require discipline to avoid collision or confusion with similarly named `regs.h` fields. MI0 busy/poll bits need correct polling by callers; the header does not enforce timing.

## Test Signals
Signals include successful FPGA board probe, readable FPGA version/status registers, working MI0 MDIO reads/writes, GMAC enable/disable and loopback behavior, per-port MAC address programming, multicast/promiscuous/jumbo configuration, and correct FPGA master interrupt cause/enable handling for SGE, TP, MC3, GMAC, and PCIX events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/fpga_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/gmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/gmac.h

## Purpose
`gmac.h` defines the generic MAC abstraction for cxgb. It gives the core adapter code a uniform `struct cmac` and `struct cmac_ops` interface for different MAC chips, plus a shared statistics layout used by netdevice stats and ethtool.

## Important APIs, Types, and Functions
`struct cmac_statistics` contains transmit and receive RMON-style counters for octets, unicast/multicast/broadcast frames, pause frames, collisions, underruns, length/FCS/symbol/data/sequence/runt/jabber/internal errors, and jumbo frames/octets. `struct cmac_ops` is the MAC vtable: destroy/reset, interrupt enable/disable/clear/handler, RX/TX enable/disable, loopback, MTU, RX mode, speed/duplex/flow-control setters/getters, statistics update, and MAC address get/set.

`struct cmac` stores the statistics block, adapter pointer, ops pointer, and implementation-private instance pointer. `struct gmac` is a factory with a statistics-update period, `create()` callback, and board-level `reset()` callback. The header declares `t1_pm3393_ops` and `t1_vsc7326_ops`.

## Control Flow
The core driver obtains a `struct gmac` from board information, calls its factory/reset functions during module initialization, and then invokes `cmac->ops` from netdevice operations. Open calls MAC reset, address programming, RX mode programming, link start, and enable. Close disables RX/TX. Ettool and netdevice stats call `statistics_update()`. Link/pause/MTU/RX-mode changes call the appropriate vtable methods.

## State and Persistence
MAC state is runtime hardware state plus a software statistics accumulator in `struct cmac`. Implementation-specific state lives behind `cmac_instance`; for PM3393 it includes enabled direction bits, flow-control mode, and MAC address. Nothing is persisted across unload or hardware reset.

## Dependencies and Integration Points
The header includes `common.h` for `adapter_t` and `struct t1_rx_mode`. It is consumed by `cxgb2.c` and MAC implementations such as `pm3393.c` and `vsc7326.c`. It integrates with PHY link management through speed/duplex/flow-control callbacks and with ethtool through the common statistics layout.

## Risks
The vtable contract is broad and only partially implemented by some MACs, so callers must check optional callbacks such as `set_mtu` and `macaddress_set`. Statistics field ordering must stay synchronized with ethtool string/data emission in `cxgb2.c`. Implementations must preserve MAC enable state while reprogramming MTU, filters, and addresses; otherwise link traffic can be disrupted.

## Test Signals
Signals include MAC factory creation for each board type, open/close RX/TX enable sequencing, MAC address changes, multicast/promiscuous/all-multicast programming, MTU changes up to board limits, pause setting negotiation, link speed/duplex reporting, interrupt enable/clear/handler paths, and ethtool stats matching the `cmac_statistics` layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/gmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88e1xxx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88e1xxx.c

## Purpose
`mv88e1xxx.c` implements the `gphy`/`cphy_ops` driver for Marvell 88E1xxx 10/100/1000 copper PHYs used by cxgb boards. It handles PHY reset, MDIO configuration, autonegotiation, speed/duplex advertisement, loopback, link-status decoding, downshift, LEDs, and interrupt routing through Elmer0.

## Important APIs, Types, and Functions
The exported factory is `const struct gphy t1_mv88e1xxx_ops`, with `mv88e1xxx_phy_create()` and a no-op chip reset. The `mv88e1xxx_ops` vtable provides reset, interrupt enable/disable/clear/handler, autoneg enable/disable/restart, advertise, loopback, set speed/duplex, and get link status. Helper functions `mdio_set_bit()` and `mdio_clear_bit()` perform read-modify-write on standard PHY registers. `mv88e1xxx_downshift_set()` configures downshift after failed gigabit attempts.

## Control Flow
Creation allocates a `struct cphy`, initializes it with MDIO ops and the vtable, applies special 88E1111 transmitter class-A configuration on supported twisted-pair boards, enables downshift, and programs an LED mode on T2. Per-port reset sets `BMCR_RESET` and polls for completion. Autoneg enable sets crossover auto and restarts negotiation; autoneg disable forces manual MDI crossover and clears autoneg with a restart as required by Alaska PHY behavior. Advertisement writes both gigabit control and base advertisement registers.

Interrupt enable writes the PHY interrupt mask and sets Elmer0 GPIO interrupt bits; disable clears both; clear reads the PHY interrupt status and writes Elmer0 cause bits. The handler loops until no enabled cause remains, updating `cphy->state` for link and autoneg readiness and returning `cphy_cause_link_change` when link status should be re-evaluated.

## State and Persistence
Runtime state lives in the PHY hardware registers and in `struct cphy->state`. Advertisement, speed/duplex, crossover, downshift, interrupt mask, loopback, and LED configuration persist in the PHY until reset. The driver does not persist settings outside hardware.

## Dependencies and Integration Points
The file depends on `common.h`, `mv88e1xxx.h`, `cphy.h`, and `elmer0.h`. It integrates with the generic link-management path through `t1_link_start()` and `t1_link_changed()`, with MDIO through `simple_mdio_read/write()`, with board detection through `board_info()`, and with Elmer0 for interrupt routing. `cxgb2.c` sees its results through `struct link_config` and netdevice carrier updates.

## Risks
The interrupt handler appears to test link up using the PHY specific status register but compares with an interrupt bit name; that logic is hardware-sensitive and should be treated carefully during maintenance. Disabling autoneg requires manual crossover behavior that is easy to regress. The MDIO helpers ignore read/write errors, so hardware failures may silently produce stale configuration. Elmer0 interrupt bit usage differs between T1 and T2 and must remain board-aware.

## Test Signals
Signals include PHY reset completion, autoneg enable/disable/restart, forced 10/100 and attempted 1000 behavior, advertisement masks, link up/down interrupts, downshift operation, loopback toggling, LED programming on T2, `ethtool` link setting changes, MII ioctl reads/writes, and link-status decoding for speed/duplex/pause.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88e1xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88e1xxx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88e1xxx.h

## Purpose
`mv88e1xxx.h` provides register numbers and bit definitions for Marvell 88E1xxx copper PHYs. It supplements Linux MII definitions with gigabit control/status registers, Marvell-specific interrupt bits, vendor register addresses, crossover/downshift controls, and PHY-specific status decoding helpers.

## Important APIs, Types, and Functions
The header exports no functions. It defines fallback constants for `BMCR_SPEED1000`, `ADVERTISE_PAUSE`, and `ADVERTISE_PAUSE_ASYM`; gigabit registers `MII_GBCR` and `MII_GBSR`; gigabit advertisement/status bits; Marvell interrupt causes such as link change, autoneg done, speed/duplex change, FIFO events, symbol errors, and autoneg errors; vendor register numbers 16 through 30; and bitfield helpers for MDI crossover mode, downshift enable/count, and PHY specific status fields for pause, link, resolved status, duplex, speed, cable length, and related state.

## Control Flow
There is no control flow in the header. `mv88e1xxx.c` uses these definitions to compose MDIO register writes for advertisement, speed/duplex, crossover, downshift, loopback, and interrupts, and to decode link status during interrupt handling and `get_link_status()`.

## State and Persistence
The state represented is PHY hardware state: advertisement registers, interrupt masks/status, vendor-specific control/status, LED controls, downshift configuration, and extended registers. The header owns no software state.

## Dependencies and Integration Points
It integrates with `mv88e1xxx.c`, `cphy.h` MDIO wrappers, Linux MII register definitions, and cxgb board initialization. Constants such as `V_PSSR_LINK`, `G_PSSR_SPEED()`, `V_DOWNSHIFT_ENABLE`, and `V_PSCR_MDI_XOVER_MODE()` are central to link management and ethtool link-setting behavior.

## Risks
Incorrect bit definitions cause misreported link status, wrong advertised capabilities, missed link-change interrupts, or bad crossover/downshift programming. Fallback definitions can diverge from newer kernel headers if assumptions change. The header does not encode which Marvell PHY revisions support each vendor register, so callers must keep board/chip checks in implementation code.

## Test Signals
Signals include correct `get_link_status()` speed/duplex/pause decoding, interrupt masks matching expected hardware events, advertisement register contents for ethtool-requested modes, downshift enable and count fields, crossover auto/manual behavior, and compatibility with kernel MII definitions on all configured builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88e1xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88x201x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88x201x.c

## Purpose
`mv88x201x.c` implements the cxgb `gphy` driver for Marvell 88x201x 10G PHYs. It manages LASI link-change interrupts, link-status reads, LED control, XFP clock enablement, chip reset through Elmer0 GPIO, and fixed 10Gb full-duplex flow-control reporting.

## Important APIs, Types, and Functions
The exported factory is `const struct gphy t1_mv88x201x_ops`. The `mv88x201x_ops` vtable provides destroy, port reset, interrupt enable/disable/clear/handler, link status, loopback stub, and MMD capability bits for PMA/PMD, PCS, PHYXS, and WIS. Helpers `led_init()` and `led_link()` program LED behavior through MDIO MMD registers.

## Control Flow
Creation allocates `struct cphy`, initializes MDIO state, enables the XFP clock by setting a PCS vendor register bit, clears stale link status from PMA/PMD and PCS status registers, and initializes LED mapping. Chip reset toggles Elmer0 GPIO bit 2 low/high with 100 ms and 1 s waits, then enables the laser with GPIO bit 15. Interrupt enable programs PMA LASI control for link alarm and enables Elmer0 GPIO bit 6; disable clears both. Clear performs the required multi-read sequence for the 88x2010 Rev C link-status bug, reads LASI status, and clears Elmer0 cause. The handler clears interrupts and reports link change.

## State and Persistence
Hardware state includes the XFP clock-enable bit, LASI interrupt control/status, link LED bit, and Elmer0 GPIO reset/laser state. Software state is only the `struct cphy` allocation; no persistent configuration is stored outside hardware.

## Dependencies and Integration Points
The file depends on `cphy.h` and `elmer0.h`, plus Linux MDIO MMD constants. It integrates with cxgb link management through `cphy_ops.get_link_status()` and interrupt handler return values. Elmer0 GPIO connects the PHY reset, laser enable, and external interrupt line to the adapter.

## Risks
The PHY has documented link-status read-order bugs; simplifying the clear sequence can leave interrupts uncleared or link status stale. Loopback is a stub, so callers expecting functional PHY loopback will get success without hardware change. Link status is reported as fixed 10G/full with RX/TX pause regardless of negotiated details, which is correct for this hardware path but risky if reused for another PHY. Reset timings are long and board-specific.

## Test Signals
Signals include successful XFP clock enable, reset/laser sequencing, LASI link-change interrupt delivery and clearing, link LED on/off with carrier, fixed 10G full-duplex ethtool reporting, no stuck interrupts under link flapping, and clean destroy on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/mv88x201x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/my3126.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/my3126.c

## Purpose
`my3126.c` implements the cxgb `gphy` driver for the Myson/SMSC MY3126 10G PHY path. It uses polling rather than real PHY interrupts to detect link changes and toggle activity/link LEDs through Elmer0 GPIO while reporting a fixed 10Gb full-duplex link mode.

## Important APIs, Types, and Functions
The exported factory is `const struct gphy t1_my3126_ops`. The `my3126_ops` vtable provides destroy, reset stub, interrupt enable/disable/clear, interrupt handler, link-status getter, loopback stub, and PMA/PMD/PCS/PHYXS MMD support bits. `my3126_poll()` is a delayed-work callback that runs the interrupt-handler logic periodically. `my3126_phy_reset()` performs chip reset and laser enable through Elmer0 GPIO.

## Control Flow
Creation allocates a `struct cphy`, initializes MDIO access and delayed work, and clears cached BMSR state. Interrupt enable schedules `phy_update` at `HZ/30` and snapshots Elmer0 GPO. Disable cancels delayed work synchronously. The handler checks PMA/PMD link status every 50 polls, compares it with cached `bmsr`, and calls `t1_link_changed()` on transitions. Each poll also snapshots SUNI MSTAT activity counters, reads Elmer0 GPO, toggles activity GPIO bits based on counter movement and board type, updates cached activity state, and returns link-change cause. `get_link_status()` reads PMA/PMD status, updates link LED GPIO state, and reports speed/duplex/pause.

## State and Persistence
Software state lives in `struct cphy`: delayed work, cached BMSR, poll count, last activity count, activity LED state, and cached Elmer0 GPIO. Hardware state includes MDIO status registers and Elmer0 GPIO bits controlling reset, laser, link LED, and activity LED. Nothing persists across unload.

## Dependencies and Integration Points
The file depends on `cphy.h`, `elmer0.h`, and `suni1x10gexp_regs.h`. It uses MDIO MMD access for link status and TPI access for SUNI activity counters and Elmer0 GPIO. It integrates with core link management through `t1_link_changed()` and with board-specific behavior through `is_T2()` and `t1_is_T1B()`.

## Risks
Polling at `HZ/30` and only checking link every 50 polls can delay link transition detection. The handler returns `cphy_cause_link_change` every poll even when only LED state changes, so callers must tolerate noisy causes. MDIO/TPI read errors are ignored. LED and laser GPIO bits are board-specific magic values; reuse on another board could toggle the wrong signal. Loopback and port reset are stubs.

## Test Signals
Signals include delayed work scheduling/cancellation on interface up/down, link transition detection within expected polling latency, LED state changes for link and activity on T1B/T2, stable fixed 10G full-duplex pause reporting, reset/laser GPIO sequencing, and no delayed-work use-after-free during module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/my3126.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/pm3393.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/pm3393.c

## Purpose
`pm3393.c` implements the generic MAC interface for the PMC/Sierra PM3393 10Gb MAC/PHY device used on Chelsio boards. It handles TPI register access, PM3393 reset and initialization sequencing, RX/TX enable/disable, MTU, multicast/promiscuous filtering, flow control, MAC address programming, interrupt clearing, and RMON statistics accumulation.

## Important APIs, Types, and Functions
The exported `const struct gmac t1_pm3393_ops` provides a 15-minute statistics-update period, `pm3393_mac_create()`, and `pm3393_mac_reset()`. The `pm3393_ops` vtable implements the `cmac_ops` contract. Private `struct _cmac_instance` stores enabled direction bits, flow-control flags, and MAC address. `pmread()`/`pmwrite()` access PM3393 registers through TPI with the SUNI register offset shifted by two.

Important implementation functions include `pm3393_interrupt_enable/disable/clear/handler()`, `pm3393_enable_port()`, `pm3393_disable()`, `pm3393_set_mtu()`, `pm3393_set_rx_mode()`, `pm3393_set_speed_duplex_fc()`, `pm3393_update_statistics()`, and `pm3393_macaddress_set()`.

## Control Flow
MAC reset toggles the PM3393 reset pin through Elmer0 GPIO, waits for required analog/digital stabilization intervals, reads device status, checks PL4 reset completion/out-of-lock bits and XAUI lock, and retries up to three times. Creation allocates the `struct cmac` plus private instance, initializes default pause, and writes a long sequence of PM3393 PL4/EFLX/IFLX/TXXG/RXXG/filter tuning registers.

When the port is enabled, stats are cleared, RX/TX paths are programmed, and `t1_link_changed()` is forced because the PHY does not independently report link. RX mode changes disable RX if needed, clear promiscuous/multicast hash bits, compute multicast CRC hash filters, then restore RX. MTU and MAC address changes similarly disable active directions, program PM3393 registers, then re-enable. Statistics update snapshots MSTAT counters, reads rollover registers, reconstructs 40-bit counters, and stores them in `cmac->stats`.

## State and Persistence
Runtime software state is `cmac->stats` plus PM3393 instance fields for enabled directions, pause configuration, and MAC address. Hardware state includes PM3393 PL4/FIFO/XAUI/MAC/filter/counter registers and Elmer0 reset/interrupt bits. Statistics are accumulated in software but reset when the MAC is recreated or port stats are cleared.

## Dependencies and Integration Points
The file depends on `common.h`, `regs.h`, `gmac.h`, `elmer0.h`, `suni1x10gexp_regs.h`, CRC32, and slab allocation. `cxgb2.c` calls the MAC ops for open/close, stats, MTU, RX mode, MAC address, and pause. Interrupt paths route PM3393 external interrupts through Elmer0 and PL external interrupt bits.

## Risks
The initialization sequence contains many hard-coded vendor register writes, including undocumented values; accidental changes are high risk. Interrupt enable writes block masks but leaves global PM3393 interrupt disabled due to known persistent errors, so enabling it without fixing root cause could create interrupt storms. RMON counter reconstruction depends on clear-on-read rollover behavior and field widths. Multicast hash programming must keep ethtool/netdevice RX modes synchronized while the MAC is temporarily disabled. `pm3393_destroy()` frees only the combined allocation, so instance layout assumptions matter.

## Test Signals
Signals include successful PM3393 reset within three attempts, stable PL4/XAUI lock, port open/close traffic, MAC address filtering including broadcast exact match, multicast hash and promiscuous/all-multicast modes, jumbo MTU programming, pause changes, RMON counter growth and rollover, external interrupt clear behavior, and no packet loss caused by enable/disable reconfiguration sequences beyond expected link disruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/pm3393.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/regs.h

## Purpose
`regs.h` is the main ASIC register map for the Chelsio cxgb T1/T2 driver. It defines MMIO and PCI configuration offsets plus bitfield helpers for SGE DMA, MC3/MC4 memory controllers, TPI, TP offload engine, RAT routing, CSPI/ESPI, ULP, PL interrupt routing, MC5 TCAM, and PCI/PCI-X configuration.

## Important APIs, Types, and Functions
The file exports no functions. Its API is the macro namespace: address macros prefixed `A_`, shift macros `S_`, masks `M_`, value constructors `V_`, getters `G_`, and single-bit flags `F_`. Important blocks include `A_SG_*` for command/free/response queues, doorbells, interrupt timers, and SGE interrupt causes; `A_MC3_*` and `A_MC4_*` for memory timing/ECC/BIST/backdoor access; `A_TPI_*` for indirect external-chip access; `A_TP_*` for TOE/checksum/offload/timer/QoS/MTU/drop configuration; `A_RAT_*` for route table and framing errors; `A_CSPI_*` and `A_ESPI_*` for SPI4 datapaths; `A_ULP_*` for ULP parity/sync errors; `A_PL_ENABLE`/`A_PL_CAUSE` for top-level interrupts; `A_MC5_*` for TCAM and DBGI access; and `A_PCICFG_*` for VPD, PM CSR, interrupt cause, and PCI mode.

## Control Flow
There is no executable flow, but many driver flows are built from these constants. SGE setup writes queue base/size/credit/control registers. Interrupt paths read/write SGE, ESPI, PL, TP, ULP, RAT, MC, and PCI cause/enable registers. Ettool register dump uses ranges from this map. ESPI initialization configures `A_ESPI_*`, T2 TRICN command/status, and monitored-counter fields. PCI reset writes `A_PCICFG_PM_CSR`.

## State and Persistence
The header represents hardware state in adapter registers. Register contents persist while the device is powered and not reset; driver software shadows only selected fields such as SGE control and ESPI misc control. The header itself has no memory or persistence.

## Dependencies and Integration Points
Nearly every cxgb implementation file includes `regs.h`: `cxgb2.c` for register dumps/reset, `sge.c` for DMA and interrupt registers, `espi.c` for ESPI programming, `pm3393.c` for PL external interrupt routing, and common initialization/interrupt modules for memory/TP/RAT/MC5/PCI handling. It is the common contract between software and T1/T2 hardware documentation.

## Risks
This file is high blast-radius: wrong constants can corrupt DMA rings, mask fatal interrupts, misconfigure memory controllers, or break offload behavior. Similar field names appear in multiple blocks, so callers must use the correct address and bit namespace. Some registers have write-one-to-clear semantics, some are read-clear, and some require timing/polling; the macros do not encode those semantics. Endianness and register width assumptions must match MMIO accessors in callers.

## Test Signals
Signals include successful hardware initialization, ethtool register dump ranges returning sane values, SGE TX/RX traffic, interrupt enable/clear for SGE/ESPI/PL/TP/MC/PCI errors, TPI external-chip access, TP checksum offload, ESPI monitor reads, PCI VPD/PM reset behavior, and no regressions across T1B/T2 and FPGA/ASIC board variants after changing any register definition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/sge.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/sge.c

## Purpose
`sge.c` implements the Scatter Gather Engine for cxgb: coherent DMA command queues, receive free lists, response queue processing, NAPI receive, transmit descriptor construction, interrupt handling, TX reclamation, VLAN/checksum/TSO CPL header handling, T2 multi-port TX scheduling, and ESPI stuck-packet workarounds.

## Important APIs, Types, and Functions
Public APIs include `t1_sge_create()`, `t1_sge_configure()`, `t1_sge_destroy()`, `t1_sge_start()`, `t1_sge_stop()`, `t1_sge_intr_enable/disable/clear()`, `t1_sge_intr_error_handler()`, `t1_sge_get_intr_counts()`, `t1_sge_get_port_stats()`, `t1_sge_set_coalesce_params()`, `t1_vlan_mode()`, `t1_poll()`, `t1_interrupt()`, `t1_interrupt_thread()`, `t1_start_xmit()`, and `t1_sched_update_parms()`.

Important private types are hardware descriptors `cmdQ_e`, `freelQ_e`, and `respQ_e`; software context entries `cmdQ_ce` and `freelQ_ce`; ring structs `cmdQ`, `freelQ`, `respQ`; the T204 scheduler `sched`/`sched_port`; and main `struct sge`, which owns rings, timers, counters, per-CPU port stats, shadow control, and workaround SKBs.

## Control Flow
Creation allocates the SGE, per-port per-CPU stats, TX reclaim timer, optional T2 ESPI workaround timer, and optional multi-port TX scheduler, then suggests default queue sizes and coalescing values. Configure allocates coherent RX/TX rings, software context arrays, programs MMIO queue registers, initializes SGE control flags, and computes jumbo buffer capacity. Start refills both free lists, enables SGE control, doorbells freelists, and starts timers. Stop disables SGE, deletes timers, kills scheduler tasklet, and frees workaround SKBs.

Receive flow starts in hard IRQ. If a response is pending, pure responses may be consumed immediately; data responses schedule NAPI. `process_responses()` batches command-queue credit updates, handles pure responses, converts data responses into SKBs with `get_packet()`, processes CPL RX metadata, sets checksum/VLAN state, and calls `netif_receive_skb()`. It refills freelists and returns response credits to hardware.

Transmit flow begins in `t1_start_xmit()`, which adds CPL TX or LSO headers, handles VLAN/checksum metadata, drops invalid packet sizes, captures ARP SKBs for the ESPI workaround, and calls `t1_sge_tx()`. `t1_sge_tx()` reclaims completed descriptors, checks ring credits, optionally queues through the T204 scheduler, reserves descriptor slots, writes DMA descriptors, and rings the command queue doorbell. Timers reclaim TX buffers and inject workaround packets when ESPI monitor counters indicate stuck packets.

## State and Persistence
State is runtime-only: ring producer/consumer indexes, generation bits, DMA mappings, SKB ownership, free-list credits, command-queue processed/cleaned counters, stopped TX queues, interrupt/error counters, per-CPU port stats, timers, scheduler quotas, and workaround SKB references. Hardware queue base/size/credit/control registers mirror the software ring state until reset.

## Dependencies and Integration Points
The file depends on Linux PCI DMA, NAPI, IRQ, timers, tasklets, SKB, VLAN, checksum, TCP/IP, ARP, per-CPU, and netdevice APIs. Internal dependencies include `common.h`, `cpl5_cmd.h`, `sge.h`, `regs.h`, and `espi.h`. `cxgb2.c` uses this module for netdev TX, NAPI poll, interrupt handlers, ethtool counters, VLAN mode, and card start/stop. ESPI monitor APIs are used for T2 workarounds.

## Risks
This is the most concurrency- and memory-sensitive file in the group. Risks include DMA mapping leaks or double-unmaps, ring generation-bit mistakes, queue full/wake races, NAPI scheduling edge cases, timer use-after-free, `skb` reference leaks in ESPI workaround storage, and hardware fatal errors that suspend operation. `tx_sched_stop()` purges `s->p[s->port].skbq` inside a loop instead of `s->p[i].skbq`, which is suspicious. TX descriptor splitting for `PAGE_SIZE > 16K` and CPL header headroom handling need careful coverage. The interrupt path's manual `napi_enable()` undo after `napi_schedule_prep()` is subtle.

## Test Signals
Signals include sustained RX/TX traffic, checksum offload, TSO, VLAN insert/extract, jumbo frames, low-memory RX buffer refill behavior, TX queue stop/wake, descriptor wraparound, large-page skb fragments, NAPI budget boundaries, pure-response hardirq handling, fatal SGE interrupt handling, coalescing updates, multi-port T204 scheduling fairness, TX reclaim timer behavior, ESPI workaround timer behavior, and module unload under traffic without DMA or SKB leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/sge.c -->

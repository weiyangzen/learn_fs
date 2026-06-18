# subset-b-004304 research

Grouped research for the requested mux and net driver files. Each file section preserves the source path in its title and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mux/Kconfig

Purpose: defines the kernel configuration surface for the generic multiplexer subsystem and its controller drivers. `MULTIPLEXER` is an internal bool selected by `MUX_CORE`; `MUX_CORE` exposes the framework; the driver menu is gated by `if MULTIPLEXER`.

Important symbols: `MUX_ADG792A` depends on `I2C`; `MUX_ADGS1408` depends on `SPI`; `MUX_GPIO` depends on `GPIOLIB || COMPILE_TEST`; `MUX_MMIO` depends on `OF` and selects `REGMAP_MMIO`. The help text documents module names (`mux-adg792a`, `mux-adgs1408`, `mux-gpio`, `mux-mmio`) and the core abstraction: muxes controlled by GPIO, MMIO/regmap, or dedicated chips.

Control flow and integration: this file has no runtime flow, but it controls which objects in the sibling Makefile are built and which dependencies are forced into the build. Device-tree users typically need `MUX_CORE` plus one controller driver. `MUX_MMIO`'s `REGMAP_MMIO` select is especially important because `mmio.c` can create a regmap over mapped registers.

State and persistence: Kconfig selections persist in the kernel `.config`; there is no runtime state. Risks are dependency mismatch and hidden build coverage: `MUX_CORE` selects `MULTIPLEXER`, but selecting a leaf driver without the matching bus support is blocked by dependencies. Test signals are `scripts/kconfig` dependency checks, `make olddefconfig`, and build combinations for built-in and module leaf drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mux/Makefile

Purpose: maps mux Kconfig symbols to kernel objects. It builds `mux-core.o` from `core.o` whenever `CONFIG_MULTIPLEXER` is enabled and adds one object per hardware controller driver.

Important build variables: `mux-core-objs := core.o`, `mux-adg792a-objs := adg792a.o`, `mux-adgs1408-objs := adgs1408.o`, `mux-gpio-objs := gpio.o`, and `mux-mmio-objs := mmio.o`. `obj-$(CONFIG_...)` lines tie those aggregate objects to Kconfig symbols. The module names match the Kconfig help text.

Control flow and integration: there is no runtime flow. Build integration is direct: `CONFIG_MUX_*` produces loadable modules or built-ins according to tristate selection, while `CONFIG_MULTIPLEXER` controls the framework object. A driver object relies on exported symbols from `core.c`, so module dependency generation must see `mux-core`.

State and persistence: build state is captured by `.config`, generated `.o` and `.ko` artifacts, and module dependency metadata. Risks include stale Kconfig to Makefile mismatch if a symbol or object name changes. Test signals are `make drivers/mux/`, `make M=drivers/mux`, `modinfo` for module aliases, and allmodconfig build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/adg792a.c -->
# sources/distributed-fs/ceph-client/drivers/mux/adg792a.c

Purpose: I2C mux-controller driver for Analog Devices ADG792A/ADG792G triple 4:1 analog multiplexers. It supports either one controller that drives all three muxes in parallel or three independently addressable controllers, selected by `#mux-control-cells`.

Important APIs and functions: `adg792a_write_cmd()` writes SMBus byte data and controls active-low reset through `ADG792A_RESETB`; `adg792a_set()` implements `struct mux_control_ops.set`; `adg792a_probe()` validates SMBus byte-data support, parses device properties, allocates a `mux_chip`, initializes idle states, resets/disables the chip, and registers with `devm_mux_chip_register()`. The driver exports I2C IDs and OF compatibles `adi,adg792a` and `adi,adg792g`.

Control flow: probe checks adapter capability, reads `#mux-control-cells`, allocates either 1 or 3 controllers, sends `ADG792A_DISABLE_ALL` with reset asserted, reads optional `idle-state`, validates each controller state against 4 available states, and registers. At runtime, mux-core calls `adg792a_set()`, which chooses all-channel commands for parallel mode or per-controller commands using `mux_control_get_index()`.

State and dependencies: persistent state is in mux-core fields (`states`, `idle_state`, cached state), not private driver data. Hardware state lives in the chip command latch. Dependencies are I2C, firmware properties, `linux/mux/driver.h`, and mux-core lifetime management. Risks include invalid `idle-state` handling: the switch accepts `0 ... 4` although `states` is 4, so state 4 is allowed as an idle property even though normal select validation would reject it. Test signals are I2C probe failure paths, property variants for one versus three controllers, disconnect idle behavior, and SMBus write error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/adg792a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/adgs1408.c -->
# sources/distributed-fs/ceph-client/drivers/mux/adgs1408.c

Purpose: SPI mux-controller driver for Analog Devices ADGS1408 8:1 and ADGS1409 dual 4:1 switch devices, exposed as a single mux controller through mux-core.

Important APIs and functions: `adgs1408_spi_reg_write()` writes a two-byte SPI register transaction using `spi_write_then_read()`. `adgs1408_set()` encodes `MUX_IDLE_DISCONNECT` as disable or a selected state as `((state << 1) | 1)`. `adgs1408_probe()` gets match data, allocates one `mux_chip`, disables the switch, parses `idle-state`, sets `mux->states` to 8 for ADGS1408 or 4 for ADGS1409, validates idle state, and registers. Match tables cover SPI names and OF compatibles `adi,adgs1408` and `adi,adgs1409`.

Control flow: all state changes route through the mux-core `.set` callback. Probe initializes hardware to disabled before publishing the controller, preventing stale switch routing from being exposed. Runtime set operations are single register writes to `ADGS1408_SW_DATA`.

State and dependencies: the driver has no private state beyond match-derived chip identity during probe. Mux state lives in mux-core and device registers. It depends on SPI, firmware match data, and mux-core. Risks include the generic idle-state switch accepting `0 ... 7` before checking `idle_state < mux->states`, so ADGS1409 rejects 4-7 but ADGS1408 accepts them. SPI write failures are returned directly; there is no readback verification. Test signals include OF/SPI match data, state range for both chip IDs, disabled idle mode, and module autoload aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/adgs1408.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/core.c -->
# sources/distributed-fs/ceph-client/drivers/mux/core.c

Purpose: implements the generic Linux mux subsystem used by mux controller drivers and consumers. It provides mux-chip allocation/registration, controller selection and deselection, OF lookup of mux controls/states, resource-managed helpers, and module/class lifetime.

Important APIs and types: `struct mux_chip`, `struct mux_control`, and private `struct mux_state` represent providers, individual controllers, and consumer-bound requested states. Exported provider APIs include `mux_chip_alloc()`, `devm_mux_chip_alloc()`, `mux_chip_register()`, `devm_mux_chip_register()`, `mux_chip_unregister()`, and `mux_chip_free()`. Exported consumer APIs include `mux_control_get()`, `mux_control_get_optional()`, `devm_mux_control_get()`, `mux_control_put()`, `devm_mux_state_get*()`, `mux_control_select_delay()`, `mux_control_try_select_delay()`, `mux_control_deselect()`, `mux_state_select_delay()`, and `mux_state_deselect()`.

Control flow: `subsys_initcall(mux_init)` registers class `mux` and initializes an IDA. Providers allocate a `mux_chip`, fill per-controller `states` and `idle_state`, set ops, then register; registration applies non-cached idle states before `device_add()`. Consumers resolve phandles from `mux-controls` or `mux-states`, optionally by names, and get a controller reference from the class device. Selection takes a semaphore, validates state, skips writes when `cached_state` already matches, calls provider `.set`, records `last_change`, delays if requested, and leaves the lock held until deselect. Deselect optionally returns to configured idle state and always releases the semaphore.

State and persistence: runtime state is in `cached_state`, `idle_state`, `last_change`, per-controller semaphore, class device reference count, and devres records. There is no disk persistence. Dependencies are the driver core, OF phandles, IDA, devres, and provider `.set` callbacks. Risks include consumer deadlock or stuck muxes if successful selects are not paired with deselects, invalid firmware cells, stale cached state after provider write errors, and provider failure during idle restoration. Test signals include KUnit or driver tests for OF parse edge cases, optional getters, semaphore contention (`try_select` returns `-EBUSY`), idle restore on deselect, devm cleanup ordering, and provider error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/gpio.c -->
# sources/distributed-fs/ceph-client/drivers/mux/gpio.c

Purpose: platform driver for muxes controlled by an array of GPIO lines. It exposes one mux controller whose state value is driven as a binary value across the GPIO array.

Important APIs and functions: `struct mux_gpio` stores `struct gpio_descs *gpios`. `mux_gpio_set()` converts the integer state into a bitmap with `bitmap_from_arr32()` and writes all GPIOs through `gpiod_multi_set_value_cansleep()`. `mux_gpio_probe()` counts `"mux"` GPIOs, allocates a `mux_chip`, retrieves the GPIO array as outputs initially low, sets `states = BIT(pins)`, validates optional `idle-state`, optionally enables a `"mux"` regulator, and registers the mux chip. OF compatible is `gpio-mux`.

Control flow: probe constructs the controller from firmware-described GPIOs; runtime selection is a pure GPIO write path invoked by mux-core. Regulator enable happens before registration so consumers do not see an unpowered mux. Idle restoration is performed by mux-core when configured.

State and dependencies: persistent runtime state is held by mux-core and GPIO descriptor ownership; hardware state is GPIO output level. Dependencies are GPIOLIB, platform bus, firmware properties, optional regulator framework, and mux-core. Risks include `BIT(pins)` overflow for large GPIO arrays, ambiguous GPIO bit ordering if firmware authors do not match hardware wiring, and no explicit handling of `MUX_IDLE_DISCONNECT` because GPIO muxes support only numeric states or `AS_IS`. Test signals include DT GPIO count/order, idle-state boundary checks, regulator probe deferral, state-to-line mapping, and suspend/resume behavior inherited from GPIO providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/mmio.c -->
# sources/distributed-fs/ceph-client/drivers/mux/mmio.c

Purpose: platform driver for mux controllers represented by contiguous bitfields in memory-mapped or parent regmap registers. It supports compatible strings `mmio-mux` and `reg-mux`.

Important APIs and functions: `struct mux_mmio` stores one `regmap_field *` per controller and saved `hardware_states` for suspend. `mux_mmio_get()` and `mux_mmio_set()` read/write a controller bitfield. `mux_mmio_probe()` obtains a regmap from a parent syscon for `mmio-mux`, from a mapped resource for `reg-mux`, or from the parent device as fallback. It parses `mux-reg-masks` pairs of register and mask, validates contiguous masks with `GENMASK(fls(mask)-1, ffs(mask)-1)`, allocates regmap fields, computes `states = 1 << width`, parses optional `idle-states`, and registers. NOIRQ PM callbacks save and restore all bitfields.

Control flow: probe maps firmware bitfield definitions into mux-core controllers. Runtime set operations are regmap field writes. Suspend reads each current hardware field into `hardware_states`; resume writes them back before normal interrupt-time activity resumes.

State and dependencies: state is split among mux-core cached state, regmap hardware fields, and suspend snapshots. Dependencies include OF, syscon, platform resources, regmap, and PM sleep callbacks. Risks include invalid zero or non-contiguous masks, bit width overflow in `1 << bits` if unusually wide fields are described, parent regmap fallback ambiguity, and resume failure leaving hardware routing changed. Test signals include DT validation for `mux-reg-masks`, syscon and direct MMIO variants, idle-state range, suspend/resume with changed register contents, and regmap error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mux/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/Kconfig

Purpose: top-level Kconfig for Linux network device support in this source tree. It defines `NETDEVICES`, the `NET_CORE` submenu, many virtual/core device options, and sources subordinate driver-family Kconfig files, including ARCNET.

Important symbols in scope: `NETDEVICES` depends on `NET`; `NET_CORE` gates core virtual/networking drivers. The requested code is directly tied to `AMT`, which depends on `INET && IP_MULTICAST` and selects `NET_UDP_TUNNEL`, and `NETDEV_LEGACY_INIT`, which depends on `ISA` and enables `Space.o`. `source "drivers/net/arcnet/Kconfig"` pulls in the ARCNET driver family. Other symbols in this file establish neighboring build context for VXLAN, GENEVE, GTP, TUN/TAP, veth, Xen, vmxnet3, and netdevsim.

Control flow and integration: this file has no runtime control flow. It controls whether the Makefile builds `amt.o`, `Space.o`, and the `arcnet/` subdirectory. AMT becomes a module named `amt` and exposes rtnetlink link kind `"amt"` at runtime. `NETDEV_LEGACY_INIT` exists to retain old ISA boot-time probing helpers.

State and persistence: selections persist in `.config`; source inclusions define the configuration tree. Risks include dependency changes that allow build without required network stack pieces, and broad top-level edits causing unrelated driver churn. Test signals are `allmodconfig`, `allyesconfig`, `randconfig` around `AMT`, `ARCNET`, `NETDEV_LEGACY_INIT`, and link-time dependency checks for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/Makefile

Purpose: top-level build manifest for network device drivers. It maps configuration symbols to object files or subdirectories.

Important build entries in scope: `obj-$(CONFIG_AMT) += amt.o` builds the AMT virtual tunnel driver; `obj-$(CONFIG_NETDEV_LEGACY_INIT) += Space.o` builds boot-time legacy probe support; `obj-$(CONFIG_ARCNET) += arcnet/` descends into the ARCNET Makefile. The file also unconditionally descends into some core PHY-related folders via `obj-y` and conditionally includes many network families.

Control flow and integration: no runtime control flow exists. Build integration is symbol-driven; Kconfig controls whether each object is built-in or modular. The ARCNET subdirectory has a second Makefile that maps packet format and chipset options. AMT builds as one object and exports the rtnetlink alias through module metadata.

State and persistence: state is generated build output and module metadata. Risks include mismatched Kconfig/Makefile names, missing subdirectory inclusion, and unintentionally building legacy `Space.o` outside ISA configs. Test signals are targeted `make drivers/net/amt.o`, `make drivers/net/Space.o`, `make drivers/net/arcnet/`, full `M=drivers/net` module builds, and checking generated modules for expected names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/Space.c -->
# sources/distributed-fs/ceph-client/drivers/net/Space.c

Purpose: legacy network-device boot configuration and ISA autoprobe support. It parses `netdev=` and `ether=` boot parameters, stores up to eight device setup records, and runs a small legacy Ethernet probe sequence during init.

Important APIs and functions: `struct netdev_boot_setup` stores a device name and `struct ifmap`. `netdev_boot_setup_add()` writes into the static setup table. `netdev_boot_setup_check()` is exported and copies boot-time IRQ, base address, and memory range into a matching `net_device`. `netdev_boot_base()` returns a configured base address or 1 when the device already exists. `netdev_boot_setup()` parses numeric boot options with `get_options()`. `probe_list2()` calls legacy probe callbacks and records failed autoprobes. `ethif_probe2()` and `net_olddevs_init()` try `eth0` through `eth7`.

Control flow: early boot `__setup` handlers populate `dev_boot_setup`. Later `device_initcall(net_olddevs_init)` loops through legacy units, obtains any configured base, and tries the compiled-in `isa_probes` list. Drivers can call `netdev_boot_setup_check()` during probe to consume stored settings.

State and dependencies: all persistent runtime state is the static `dev_boot_setup[8]` table and per-probe failure status in `isa_probes`. Dependencies include legacy ISA probe symbols such as `ne_probe` and `cs89x0_probe` when configured, `init_net`, and boot parameter parsing. Risks include fixed table capacity, old-style probing side effects on ISA I/O space, and repeated failure suppression only for autoprobes. Test signals include boot parameter parsing, exported symbol users, `NETDEV_LEGACY_INIT` builds, and ISA randconfig coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/Space.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/amt.c -->
# sources/distributed-fs/ceph-client/drivers/net/amt.c

Purpose: implements Automatic Multicast Tunneling as a virtual netdevice with gateway and relay modes. Gateways encapsulate listener IGMP/MLD reports toward relays and decapsulate multicast data; relays answer discovery/request messages, track downstream multicast membership, and encapsulate multicast data toward gateways.

Important APIs and functions: module init registers a netdevice notifier and rtnetlink link ops for kind `"amt"`, then allocates workqueue `amt`. `amt_newlink()` validates netlink attributes, binds to an Ethernet stream device, sets role-specific MTU/headroom, initializes state, and links as an upper device. `amt_dev_open()` creates the UDP tunnel socket and starts discovery/request or secret-rotation work. `amt_dev_xmit()` handles packets emitted through the virtual device. `amt_rcv()` is the UDP encapsulation receive callback. Membership state is stored in `struct amt_tunnel_list`, `struct amt_group_node`, and `struct amt_source_node` from `include/net/amt.h`.

Control flow: gateway open schedules discovery and request work; discovery sends `AMT_MSG_DISCOVERY`, advertisement receipt validates nonce and starts requests, membership query receipt marks IPv4/IPv6 readiness and injects query packets locally, and gateway xmit encapsulates membership updates only when ready. Relay receive handles discovery by sending advertisements, request by creating or refreshing a tunnel and sending IGMP/MLD general queries, update by validating nonce/MAC and updating group/source state, and virtual-device xmit by forwarding matching multicast data to all interested tunnels. Event work serializes receive and retry events from a bounded ring.

State and persistence: state is in memory only: UDP socket RCU pointer, role/status, nonce, siphash key, readiness flags, timers, event ring, tunnel list, per-group source hash tables, group/source delayed timers, and GRO cells. Source nodes are RCU-freed through a global GC list. Dependencies include UDP tunnel APIs, rtnetlink, multicast helpers, IPv4 and optional IPv6 MLD, workqueues, RCU, GRO cells, and netdevice upper/lower notifications.

Risks and tests: risk centers on concurrency and protocol validation: timers run against RCU lists, event queue overflow drops packets, nonce/MAC validation gates relay updates, MTU follows lower device changes, and teardown must cancel delayed work before freeing tunnels/groups/sources. There are subtle protocol risks in MLDv1 leave host address handling and in bounded group/source limits. Test signals include iproute2 AMT link creation validation, gateway/relay handshakes, IGMPv2/v3 and MLDv1/v2 reports, malformed AMT header drops, lower-device unregister/MTU notifications, socket creation failure, workqueue teardown, and packet counters for drops/errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/amt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/Kconfig

Purpose: defines the ARCNET driver family configuration. The top-level `ARCNET` menuconfig depends on `NETDEVICES`, a supported bus (`ISA || PCI || PCMCIA`), and `HAS_IOPORT`, then exposes packet formats and chipset/bus drivers.

Important symbols: `ARCNET_1201`, `ARCNET_1051`, `ARCNET_RAW`, and `ARCNET_CAP` select packet encapsulation modules. `ARCNET_COM90xx`, `ARCNET_COM90xxIO`, `ARCNET_RIM_I`, and `ARCNET_COM20020` select hardware families. `ARCNET_COM20020` depends on `LEDS_CLASS`; `ARCNET_COM20020_ISA`, `_PCI`, and `_CS` depend on the COM20020 core and their buses.

Control flow and integration: no runtime flow exists here. It gates the sibling Makefile and determines whether the core `arcnet.o`, protocol plug-ins, and chipset drivers are available. Help text warns that the core alone is not enough; a matching chipset driver and usually a packet format module are needed.

State and persistence: selections persist in `.config`. Risks are incomplete user configurations, especially enabling ARCNET core without a usable chipset driver or protocol format. The `LEDS_CLASS` dependency for COM20020 matters because COM20020 PCI integrates LED triggers. Test signals include Kconfig dependency checks across ISA/PCI/PCMCIA, allmodconfig builds, and module dependency generation for protocol plug-ins that use exported core symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/Makefile

Purpose: builds the ARCNET core, packet encapsulation plug-ins, and hardware drivers according to Kconfig symbols.

Important entries: `obj-$(CONFIG_ARCNET) += arcnet.o` builds the shared core. Protocol modules include `rfc1201.o`, `rfc1051.o`, `arc-rawmode.o`, and `capmode.o`. Hardware modules include `com90xx.o`, `com90io.o`, `arc-rimi.o`, `com20020.o`, `com20020-isa.o`, `com20020-pci.o`, and `com20020_cs.o`.

Control flow and integration: no runtime flow exists in the Makefile. It controls module boundaries. Packet modules register `struct ArcProto` handlers against exported maps in `arcnet.o`; bus/chipset drivers call exported allocation/open/interrupt helpers from the core and, for COM20020 ISA/PCI, shared functions in `com20020.o`.

State and persistence: build artifacts and module dependency metadata are the only state. Risks include selecting a bus front-end without the shared COM20020 core, or changing object names without Kconfig help/module alias updates. Test signals are `make M=drivers/net/arcnet`, module load/unload ordering for core plus plug-ins, and randconfig coverage for every object line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/arc-rawmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/arc-rawmode.c

Purpose: ARCNET raw packet encapsulation module. It uses only the hardware ARCNET header and no software protocol header, exposing packets as `ETH_P_ARCNET`.

Important APIs and functions: `rx()` copies a received card buffer into an skb, using ARCNET offset rules for 256-byte versus 512-byte packet layouts. `build_header()` pushes `ARC_HDR_SIZE`, fills source and destination hardware addresses, and handles loopback/noarp by using destination 0. `prepare_tx()` computes buffer offsets, writes the hardware header and raw payload to the card through `lp->hw.copy_to_card()`, and records `lastload_dest`. `rawmode_proto` supplies `.suffix = 'r'`, MTU `XMTU`, receive/build/prepare callbacks, and no continuation or ack callback.

Control flow: module init replaces default protocol-map entries with raw mode, sets broadcast protocol when no better one exists, and makes raw mode the default. ARCNET core later calls the callbacks from `arcnet_header()`, `arcnet_send_packet()`, and `arcnet_rx()`.

State and dependencies: state is global protocol-map registration plus per-device `lastload_dest`; payload state remains in skbs and card buffers. Dependencies are `arcdevice.h`, exported ARCNET protocol maps, core buffer copy hooks, and netif receive. Risks include raw mode interoperability, length/offset edge cases near `MTU`, `MinTU`, and `XMTU`, and default-protocol takeover affecting other loaded protocol modules. Test signals include module load/unload map restoration, small and extended packet receive/transmit, broadcast destination behavior, and oversized packet clamping warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/arc-rawmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/arc-rimi.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/arc-rimi.c

Purpose: hardware driver for ARCNET COM90xx RIM I cards, which are entirely memory-mapped and require explicit module or boot parameters for shared memory, IRQ, and station ID.

Important APIs and functions: `arcrimi_probe()` validates required parameters and reserves a provisional memory window. `check_mirror()` maps candidate memory regions to detect mirrored card memory. `arcrimi_found()` maps the card, requests IRQ, determines mirror range, fills `arcnet_local` hardware callbacks, remaps the final memory span, reads station ID, and registers the netdevice. Hardware callbacks implement reset, interrupt mask, status, command, and memory copies. Module init allocates an ARCNET device and calls probe; exit unregisters and releases mappings, IRQ, and memory.

Control flow: no autoprobe is attempted. Init creates `arc%d` or requested name, applies node/io/irq params, normalizes IRQ 2 to 9, probes, then leaves the registered device to use shared ARCNET core open/interrupt/transmit paths. The reset path performs a fake reset write when requested, otherwise clears reset/config flags and enables extended packets.

State and dependencies: state includes module parameters, global `my_dev`, reserved memory region, `lp->mem_start`, device IRQ, and callbacks in `arcnet_local`. Dependencies are ARCNET core, COM9026 register definitions, MMIO accessors, and legacy boot `__setup` when built-in. Risks include untested hardware path, required manual parameters, mirror probing around physical memory windows, and cleanup correctness after partial failures. Test signals are parameter parsing, memory reservation/remap failures, IRQ request failures, reset/status/command register access, and unload resource release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/arc-rimi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/arcdevice.h -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/arcdevice.h

Purpose: shared ARCNET internal header. It defines debug flags, packet size constants, hardware status/command bits, protocol plug-in contracts, per-device private state, LED event APIs, exported core helpers, and bus access macros.

Important types and macros: `struct ArcProto` is the protocol plug-in ABI with receive, header-build, transmit, continuation, and ack callbacks. `struct arcnet_local` is the private state for all ARCNET netdevices: hardware configuration, tx/rx buffer indexes, locks, LED triggers, timers, work items, reconfiguration counters, RFC1201 assembly state, outgoing packet state, hardware operation callbacks, and optional mapped memory. `Incoming` and `Outgoing` hold split-packet state. Constants define `MTU`, `MinTU`, `XMTU`, `TXFREEflag`, `TXACKflag`, `RECONflag`, `RESETflag`, `TXcmd`, `RXcmd`, `CFLAGScmd`, `NORMALconf`, `EXTconf`, and COM20020 feature flags.

Control flow and integration: the header itself has no runtime flow, but it sets the contracts between `arcnet.c`, packet modules such as raw/cap mode, and chipset drivers such as RIM I and COM20020. Hardware drivers fill `lp->hw`; the core calls those callbacks under its locking model.

State and dependencies: this header defines all persistent in-memory ARCNET state but stores none by itself. Dependencies include kernel interrupt/workqueue APIs, `linux/if_arcnet.h`, I/O accessors, and LED support. Risks are ABI coupling across many modules, flag overlap (`TESTflag` and `EXCNAKflag` both 0x08 in different contexts), buffer queue invariants, and debug macro compile-time filtering. Test signals include building every ARCNET module together, struct field use across hardware drivers, buffer queue stress, and LED trigger lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/arcdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/arcnet.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/arcnet.c

Purpose: device-independent ARCNET core. It owns protocol maps, netdevice setup, open/close, transmit, interrupt handling, receive dispatch, buffer management, LED triggers, reset recovery, and exported helpers for hardware and encapsulation modules.

Important APIs and functions: global exported maps `arc_proto_map`, `arc_proto_default`, `arc_bcast_proto`, and `arc_raw_proto` let protocol modules register. `alloc_arcdev()`/`free_arcdev()` allocate ARCNET netdevices. `arcnet_open()` resets hardware, initializes buffers and protocol defaults, enables interrupts, starts carrier timer, and starts the queue. `arcnet_send_packet()` chooses a card buffer and invokes the selected `ArcProto.prepare_tx()`. `arcnet_interrupt()` handles reset, receive, excessive NAK, transmit completion, split transmit continuation, queue wakeups, and reconfiguration/cabling state. `arcnet_rx()` copies headers and dispatches to protocol-specific receive callbacks. `arcnet_unregister_proto()` removes a protocol from all maps.

Control flow: hardware drivers register netdevices with `arcnet_netdev_ops`. On open, four card buffers enter a small circular free queue. Transmit stops the netdev queue, loads one buffer, enables TX interrupts, and the IRQ handler starts or completes actual hardware transmission. Receive IRQs rotate receive buffers before copying the completed buffer. Reset IRQs schedule work that closes and reopens the device under RTNL. Reconfiguration IRQs mark carrier down and use a timer to restore carrier after quiet time.

State and dependencies: key state is `arcnet_local`: locks, buffer queue, `cur_tx`/`next_tx`/`cur_rx`, outgoing skb/proto, reconfiguration counters, timer, work items, and hardware callbacks. Dependencies are netdevice core, skbuffs, LED triggers, workqueues, module references, and chipset callbacks. Risks include tight IRQ locking assumptions, small buffer queue invariants, transmit timeout recovery, ack/error-report work racing with skb lifetime, and protocol-map mutation by modules. Test signals include module load ordering, open/close cycles, IRQ simulation for RX/TX/RECON/RESET, tx timeout, split packet continuation, netdev stats, and protocol unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/arcnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/capmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/capmode.c

Purpose: ARCNET CAP mode encapsulation module. CAP mode adds a four-byte userspace cookie after the protocol byte and reports transmit acknowledgement status back to userspace as a received protocol-0 packet.

Important APIs and functions: `rx()` builds an skb with space for the inserted cookie and copies card data around that extra integer. `build_header()` fills the hardware header and logs the cookie. `prepare_tx()` subtracts the ARC header and cookie from the length, writes the ARC header and protocol byte, skips the cookie while copying the message body to the card, and records `lastload_dest`. `ack_tx()` creates an acknowledgement skb, copies the original header/cookie, sets CAP protocol to 0, writes the hardware ack result, feeds it through `netif_rx()`, frees the outgoing skb, and clears `lp->outgoing.proto`. `capmode_proto` provides callbacks and `XMTU`.

Control flow: module init assigns CAP mode to protocol IDs 1 through 8 if still default, potentially makes it broadcast/default/raw protocol, and exit unregisters it through the core. During transmit, ARCNET core calls `ack_tx()` after hardware completion because `capmode_proto` advertises an ack callback.

State and dependencies: persistent state is protocol-map registration and `lp->outgoing` ownership until ack completion. Dependencies are `arcdevice.h`, netdevice receive, and ARCNET core transmit completion. Risks include skb layout assumptions around the inserted cookie, double ack paths if core error-report work and CAP ack both observe the outgoing skb, and protocol-map takeover for raw/default behavior. Test signals include ack statuses 0/1/2, cookie round trip, protocol IDs 1-8, short/extended packet offsets, and unload restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/capmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020-isa.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020-isa.c

Purpose: ISA bus front-end for ARCNET COM20020 chipset devices. It handles module/boot parameters, I/O region reservation, optional IRQ autoprobe, and hands the initialized netdevice to the shared COM20020 core.

Important APIs and functions: `com20020isa_probe()` validates `dev->base_addr`, reserves `ARCNET_TOTAL_SIZE`, checks for empty I/O space, calls `com20020_check()`, performs IRQ autoprobing when no IRQ is supplied, sets card name, and calls `com20020_found(dev, 0)`. `com20020_init()` allocates an ARCNET device, sets node address, uses `com20020_netdev_ops`, fills `arcnet_local` COM20020 parameters (`backplane`, `clockp`, `clockm`, `timeout`, owner), and probes. `com20020_exit()` unregisters and releases IRQ/I/O resources. Built-in `com20020isa_setup()` parses boot arguments.

Control flow: module load creates one device from parameters; probe confirms hardware and may trigger the card to discover IRQ; shared COM20020 code then registers the netdevice and supplies the actual low-level operations. Exit assumes `my_dev` was successfully initialized and unwinds netdev, IRQ, I/O region, and memory allocation.

State and dependencies: state includes module parameters, global `my_dev`, reserved I/O port range, IRQ, node address, and shared COM20020 private fields. Dependencies are ARCNET core, `com20020.h`, ISA I/O ports, IRQ probing, and module parameter parsing. Risks include no base-address autoprobe, fragile legacy IRQ probing, single-device global design, and exit path assumptions. Test signals include valid/invalid I/O base, empty status `0xff`, IRQ 2 to 9 normalization, `com20020_check()` failure, boot parameter parsing, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020-isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020-pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020-pci.c

Purpose: PCI front-end for COM20020 ARCNET adapters, including Contemporary Controls, SOHARD, EAE PLX PCI variants, multi-channel cards, rotary-coded device IDs, backplane reporting, and optional LED class integration.

Important APIs and functions: `com20020pci_probe()` enables the PCI device, allocates `com20020_priv`, selects `com20020_pci_card_info`, reserves misc and per-channel I/O regions, allocates one ARCNET netdevice per channel, performs dummy controller access, fills `arcnet_local`, reads backplane/rotary state, validates hardware with `com20020_check()`, registers through `com20020_found(dev, IRQF_SHARED)`, and sets up optional LED class devices plus ARCNET LED triggers. `com20020pci_remove()` unregisters each channel and frees IRQ/netdevice resources. `led_tx_set()` and `led_recon_set()` drive card-specific misc I/O bits. `backplane_mode_show()` exposes backplane state in sysfs.

Control flow: PCI ID table entries carry card-info pointers that define BAR/offset/size maps, device count, LED registers, rotary offset, and speed/features. Probe loops through channels and accumulates registered devices in `priv->list_dev`; any failure calls remove to unwind already-added devices. Runtime network operation is delegated to shared COM20020 netdev ops and ARCNET core.

State and dependencies: state includes `com20020_priv`, per-channel `com20020_dev`, devres-managed I/O regions and LED strings, `arcnet_local` fields, PCI drvdata, and sysfs group attachment. Dependencies are PCI, I/O port access, LED class, ARCNET core, and shared COM20020 code. Risks include partial multi-channel probe cleanup, misc BAR assumptions for backplane/LED/rotary reads, shared IRQ handling, default node parameter applied to every channel unless rotary overrides names, and LED devres ordering versus netdevice unregister. Test signals include PCI ID matching, each card-info map, multi-channel failure injection, sysfs `backplane_mode`, LED brightness callbacks, shared IRQ registration, and module remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020-pci.c -->

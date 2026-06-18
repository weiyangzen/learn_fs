# subset-b-004699 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ppp/pppoe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ppp/pppoe.c

Purpose: implements the PPP over Ethernet PPPOX protocol module. It provides PF_PPPOX/PX_PROTO_OE socket creation, PPP channel registration, Ethernet packet receive/transmit handling for PPPoE session frames, PADT discovery handling, per-network namespace socket lookup, and optional `/proc/net/pppoe` inspection.

Important APIs and functions: `pppoe_create()` allocates `struct pppox_sock` sockets and sets `pppoe_ops`; `pppoe_connect()` binds a session ID, peer MAC, and netdevice into a PPP channel; `pppoe_release()` tears down device references, hash entries, and PPP bindings. `pppoe_rcv()` handles `ETH_P_PPP_SES`, validates PPPoE length and protocol compression, and dispatches to the matched socket. `pppoe_disc_rcv()` watches discovery frames for PADT and schedules `pppoe_unbind_sock_work()`. `__pppoe_xmit()` and `pppoe_sendmsg()` build PPPoE and Ethernet headers for PPP or socket writes. `pppoe_fill_forward_path()` exposes encapsulation metadata to forwarding offload path construction.

Control flow: module init registers per-net state, the socket proto, PX_PROTO_OE, two packet handlers, and a netdevice notifier. Session connect looks up the named device, inserts the socket into the per-net hash under `hash_lock`, initializes `struct ppp_channel`, then calls `ppp_register_net_channel()`. Receive path hashes on session ID, source MAC, and ifindex, then invokes `__sk_receive_skb()` so backlog processing either feeds `ppp_input()` for bound sockets or queues skbs for userspace. Device-down, MTU, or MAC-address changes call `pppoe_flush_dev()` to unbind all affected sockets.

State and persistence: runtime state lives in `struct pppoe_net` hash buckets, `struct pppox_sock` fields `pppoe_pa`, `pppoe_ifindex`, `pppoe_dev`, `chan`, `next`, and socket state bits. Netdevice references are held while connected, RCU protects hash readers, and a work item defers PADT unbind because channel unregister cannot run directly from packet receive context. No durable state is written.

Dependencies and integration: integrates with generic PPPoX from `pppox.c`, the PPP channel core, Ethernet packet_type dispatch, net namespaces, procfs seq files, netdevice notifiers, RCU, socket proto operations, and forwarding path infrastructure. It relies on `CONFIG_PPPOE_HASH_BITS` satisfying the compile-time hash constraint.

Risks and test signals: risks concentrate around lock ordering between socket locks and `hash_lock`, device reference balancing, RCU lifetime while proc and RX paths walk hash chains, PADT work cancellation, and MTU-derived MRU calculations. Test signals include PPPoE connect/disconnect, duplicate tuple rejection, same SID/MAC on different ifindexes, PADT-triggered unbind, device down or MTU/MAC change flushing, packet length/PFC rejection, `/proc/net/pppoe` visibility, namespace isolation, module unload, and traffic through PPP direct transmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ppp/pppoe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ppp/pppox.c -->
# sources/distributed-fs/ceph-client/drivers/net/ppp/pppox.c

Purpose: provides the generic PPPoX socket family dispatcher for PF_PPPOX. It is the registry and common ioctl layer used by protocol-specific modules such as PPPoE and PPTP.

Important APIs and functions: `register_pppox_proto()` and `unregister_pppox_proto()` publish protocol handlers in the global `pppox_protos[]` table. `pppox_create()` validates the requested protocol, requests the module alias if absent, pins the provider module, and calls the provider `create()` callback. `pppox_ioctl()` implements `PPPIOCGCHAN` generically by returning `ppp_channel_index()` and marking the socket `PPPOX_BOUND`, while delegating other ioctls to the protocol-specific handler. `pppox_unbind_sock()` unregisters an attached PPP channel and marks the socket dead. `pppox_compat_ioctl()` adapts compat pointers.

Control flow: module init registers `pppox_proto_family` with `sock_register()`. Socket creation is a two-stage dispatch: PF_PPPOX reaches `pppox_create()`, then protocol-specific code supplies actual socket operations and channel behavior. Ioctls enter through protocol socket ops but commonly call `pppox_ioctl()`, which locks the socket before inspecting or mutating state.

State and persistence: state is limited to the static protocol pointer table and transient socket state bits in `struct pppox_sock`. No synchronization is visible around table updates, so registration ordering is expected to happen during module init/exit while users rely on module refcounts. There is no persistent storage.

Dependencies and integration: depends on the socket family core, module autoload aliases, PPP channel APIs, user-copy helpers, and protocol modules that provide `struct pppox_proto`. It exports the registry and unbind/ioctl helpers for those modules.

Risks and test signals: risks include stale protocol-table access during unregister, incorrect module refcount handling around provider `create()`, and state transitions caused by `PPPIOCGCHAN`. Test signals are PF_PPPOX socket creation before and after provider module autoload, invalid protocol handling, generic channel ioctl behavior, compat ioctl coverage, provider unload/reload, and PPP channel unregister on protocol release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ppp/pppox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ppp/pptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ppp/pptp.c

Purpose: implements the Point-to-Point Tunneling Protocol data plane as a PPPoX protocol over IPv4 GRE. It creates PX_PROTO_PPTP sockets, maps local call IDs to sockets, registers a GRE protocol handler, and encapsulates/decapsulates PPP frames in PPTP GRE headers.

Important APIs and functions: `pptp_bind()` allocates or reserves a local call ID through `add_chan()`. `pptp_connect()` validates destination call/IP, routes the GRE flow, sets PPP MTU/hdrlen, and registers the PPP channel. `pptp_xmit()` builds GRE and IPv4 headers, handles PPP AC/protocol compression flags, sends ACKs, and routes via `ip_local_out()`. `pptp_rcv()` validates incoming GRE fields and finds a socket with `lookup_chan()`. `pptp_rcv_core()` updates ACK/sequence state, reconstructs PPP payloads, and feeds `ppp_input()`. `pptp_ppp_ioctl()` exposes PPP compression flag get/set.

Control flow: module init allocates the call-id array, registers the GRE handler for PPTP, registers the socket proto, then registers PX_PROTO_PPTP with PPPoX. Userspace binds a source call ID first, connects to a peer call ID and IPv4 address, then PPP traffic flows through direct channel transmit. RX enters from GRE, looks up by destination call ID and source address, then socket backlog processing validates sequencing and payload before passing data to PPP.

State and persistence: global state includes `callid_bitmap`, RCU-protected `callid_sock[]`, and `chan_lock`. Per-socket state in `struct pptp_opt` stores source/destination addresses, sent/received sequence and ACK counters, and PPP flags. Route capabilities are cached in the socket, and release/destruct paths delete call IDs and synchronize RCU. No durable state is written.

Dependencies and integration: integrates with generic PPPoX, PPP channel core, IPv4 routing, GRE protocol registration, network security flow classification, socket capabilities, netfilter connection tracking reset, and IP output. It is IPv4-only and depends on GRE/PPTP header definitions from networking headers.

Risks and test signals: risks include call-id collisions, wrap-around sequence comparisons, skb headroom reallocation ownership, route lifetime handling, unregistering channels while transmit is active, and acceptance of duplicate destination call IDs. Test signals include bind with explicit and auto call IDs, duplicate local and remote call rejection, GRE field validation drops, LCP echo handling out of order, compression flag ioctl behavior, route failure, module unload after open sockets, and packet capture confirming GRE/IP header fields and ACK behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ppp/pptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/pse-pd/Kconfig

Purpose: defines Kconfig options for Ethernet Power Sourcing Equipment support and its controller drivers.

Important options: `PSE_CONTROLLER` is a bool menu option gated by `REGULATOR` and enables the core PSE framework. `PSE_REGULATOR` builds the simple regulator-backed PoDL PSE provider. `PSE_PD692X0` enables the Microchip PD692x0 I2C PSE driver and selects `FW_LOADER` plus `FW_UPLOAD` for firmware update support. `PSE_SI3474` enables the Skyworks Si3474 I2C driver. `PSE_TPS23881` enables the TI TPS23881 I2C driver.

Control flow: the menu is visible only after `PSE_CONTROLLER`; child tristates control which objects the Makefile includes. Selecting chip drivers brings in only the subsystem dependencies listed here, while detailed runtime requirements such as regulators, firmware blobs, IRQs, and device-tree topology are enforced by the individual drivers.

State and persistence: no runtime state is stored here. The selected symbols determine whether code is built-in, modular, or omitted, and therefore whether PSE ethtool/regulator integration exists in a kernel image.

Dependencies and integration: this file connects net PSE code to the regulator, I2C, firmware loader, and firmware upload subsystems through Kconfig symbols. Driver module names are documented for modular builds.

Risks and test signals: risks are missing dependency declarations, especially firmware upload for PD692x0 or I2C for chip drivers, and user confusion from the core being bool while providers are tristate. Test signals include allmodconfig/allyesconfig coverage, `PSE_CONTROLLER=n` hiding child symbols, modular builds for each provider, and dependency checks when REGULATOR or I2C is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/pse-pd/Makefile

Purpose: maps PSE Kconfig symbols to the objects built in `drivers/net/pse-pd`.

Important build rules: `CONFIG_PSE_CONTROLLER` builds `pse_core.o`; `CONFIG_PSE_REGULATOR` builds `pse_regulator.o`; `CONFIG_PSE_PD692X0`, `CONFIG_PSE_SI3474`, and `CONFIG_PSE_TPS23881` build their corresponding I2C controller drivers.

Control flow: Kbuild includes the framework object whenever the core symbol is enabled, then adds provider objects according to individual driver symbols. Since `pse_core.o` exports symbols consumed by providers and PHY/ethtool code, the Kconfig dependency around `PSE_CONTROLLER` is the main guard against unresolved references.

State and persistence: no runtime state is defined. The file controls object inclusion and module composition only.

Dependencies and integration: integrates with the parent networking driver build and the Kconfig file in the same directory. The output objects implement the framework, a regulator-only provider, and three I2C chip providers.

Risks and test signals: risks are stale object names after source renames or Kconfig mismatches that omit the core while provider code expects exported PSE helpers. Test signals include built-in and module builds for each symbol combination, clean `modpost` symbol resolution, and confirming module names match Kconfig help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/pd692x0.c -->
# sources/distributed-fs/ceph-client/drivers/net/pse-pd/pd692x0.c

Purpose: implements an I2C PSE controller driver for Microchip PD69200/PD69210/PD69220 devices. It exposes IEEE 802.3 Clause 33 PSE operations through `pse_controller_dev`, configures manager and port matrices from device tree, manages per-manager power budgets with regulators, and supports firmware upload for controller recovery/update.

Important APIs and functions: `pd692x0_sendrecv_msg()` is the central command path, adding echo/checksum, recovering from communication loss, and validating report replies. PSE callbacks include `pd692x0_pi_enable()`, `pd692x0_pi_disable()`, `pd692x0_pi_get_admin_state()`, `pd692x0_pi_get_pw_status()`, `pd692x0_pi_get_ext_state()`, `pd692x0_pi_get_pw_class()`, `pd692x0_pi_get_actual_pw()`, power-limit range/get/set, and priority get/set. `pd692x0_setup_pi_matrix()` parses `managers` and PSE PI pairsets, registers manager regulators, requests budgets, programs the hardware matrix, and saves a user byte. Firmware upload callbacks `pd692x0_fw_prepare()`, `pd692x0_fw_write()`, `pd692x0_fw_poll_complete()`, `pd692x0_fw_cancel()`, and `pd692x0_fw_cleanup()` implement programming mode.

Control flow: probe enables `vdd` and `vdda`, checks I2C functionality, reads controller status, determines firmware state/version, initializes `pcdev`, registers the PSE controller, then registers with the firmware upload API. Normal PSE operations first call `pd692x0_fw_unavailable()` to block access while firmware is broken or updating. Configuration writes temporary matrix entries for all 48 PIs, commits them, and writes manager power banks. Removal frees manager power budgets and unregisters firmware upload.

State and persistence: `struct pd692x0_priv` stores I2C client, firmware state, upload handle, cancel flag, message ID, command pacing state, saved-configuration flag, cached admin states, manager regulator devices, requested manager budgets, manager count, and the port matrix. Hardware persistent-ish state includes the programmed port matrix, power-bank budgets, port parameters, priority, user byte, and firmware image in controller memory.

Dependencies and integration: depends on I2C, regulator framework, firmware loader/upload APIs, device tree, and PSE core. It exposes dynamic budget strategy support and priority maximum 2 to the core. It maps many controller-specific status codes to ethtool C33 extended state/substate values.

Risks and test signals: risks include checksum/echo protocol mismatch, long communication-recovery sleeps while locks are held by callers, firmware state gating that disables PSE operations, DT manager/port ordering assumptions, power budget leaks, truncation in manager regulator name formatting, and incomplete matrix/user-byte programming after firmware update. Test signals include probe with good, old, and broken firmware; firmware upload cancel/error/complete paths; manager budget request/free accounting; DT matrix validation; enable/disable/status/priority/power-limit ethtool operations; and I2C fault injection around every send/receive phase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/pd692x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/pse_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/pse-pd/pse_core.c

Purpose: provides the Linux Ethernet PSE framework. It registers PSE controllers, maps device-tree PSE references to `pse_control` handles for PHY/netdev consumers, exposes each PSE power interface as a regulator, provides ethtool get/set operations, manages PSE power domains and budgets, and converts controller IRQ events into ethtool netlink plus regulator notifications.

Important APIs and functions: exported entry points include `pse_controller_register()`, `pse_controller_unregister()`, `devm_pse_controller_register()`, `devm_pse_irq_helper()`, `of_pse_control_get()`, `pse_control_put()`, `pse_ethtool_get_status()`, `pse_ethtool_set_config()`, `pse_ethtool_set_pw_limit()`, `pse_ethtool_set_prio()`, `pse_has_podl()`, and `pse_has_c33()`. Regulator callbacks `pse_pi_enable()`, `pse_pi_disable()`, `pse_pi_is_enabled()`, voltage/current limit helpers, and the IRQ worker are the internal runtime bridge.

Control flow: controller registration initializes locks, notification FIFO/work, loads PSE PI DT descriptions and pairsets, lets drivers set up PI matrices, registers one regulator per described PI, registers power domains from shared supplies, then adds the controller to the global list. Consumers call `of_pse_control_get()` using `pses` phandles; the core translates either explicit `pse-pi` nodes or `#pse-cells` indices and obtains an exclusive regulator. Ettool config operations enable/disable regulators, set limits, or priorities. IRQ helper calls driver `map_event()`, updates software power-control state, queues netlink notifications, and calls regulator notifiers.

State and persistence: global state includes `pse_controller_list`, `pse_pw_d_map`, and their mutexes. Per-controller state includes PI descriptors, regulator devices, software admin flags, detected-PD flags, power-domain pointers, allocated mW, priority, notification FIFO, and IRQ number. `pse_control` and `pse_power_domain` use krefs. State is in memory and reflected into hardware through provider callbacks and regulator budget accounting.

Dependencies and integration: integrates with OF, PHY devices, netdevices under RTNL for notification targeting, ethtool netlink, regulator core including power-budget APIs, kfifo/workqueues, IRQ helpers, xarray, and module refcounts. Provider drivers implement `struct pse_controller_ops`; PHY/netdev code consumes `pse_control`.

Risks and test signals: risks include regulator enable-count mismatches, budget accounting rollback on set-limit failures, static priority disabling lower-priority ports unexpectedly, missing cleanup on partial register failures, notification FIFO overflow, IRQ disable ordering, and deadlocks between `pcdev->lock`, `pse_list_mutex`, RTNL, and regulator callbacks. Test signals include DT parsing with one/two pairsets and invalid pinouts, controller register/unregister with active controls, ethtool status/config/power-limit/priority operations, shared-supply power-domain budget exhaustion, IRQ detection/classification/disconnection events, netlink notifications tied to an attached PHY netdev, and provider fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/pse_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/pse_regulator.c -->
# sources/distributed-fs/ceph-client/drivers/net/pse-pd/pse_regulator.c

Purpose: implements a minimal platform PSE provider backed by a single regulator. It targets simple PoDL-style Ethernet power sourcing without automatic classification or chip-specific telemetry.

Important APIs and functions: `pse_reg_probe()` obtains the exclusive `"pse"` regulator, derives the initial admin state from `regulator_is_enabled()`, initializes `pse_controller_dev`, and registers it with the PSE core. PSE callbacks `pse_reg_pi_enable()`, `pse_reg_pi_disable()`, `pse_reg_pi_get_admin_state()`, and `pse_reg_pi_get_pw_status()` toggle/read the regulator and report PoDL admin/power status.

Control flow: platform probe requires an OF node compatible with `"podl-pse-regulator"`. After registration, the PSE core creates a PI regulator for consumers. Enable/disable requests from ethtool or regulator users call through the core into this driver, which directly enables or disables the underlying supply and updates cached admin state. Power status is simply delivering when the regulator is enabled and disabled otherwise.

State and persistence: `struct pse_reg_priv` stores the embedded `pse_controller_dev`, the backing regulator pointer, and cached PoDL admin state. There is no chip memory, port matrix, interrupt state, or durable persistence beyond the actual regulator output state.

Dependencies and integration: depends on platform driver binding, OF, regulator consumer APIs, and PSE core. It advertises `ETHTOOL_PSE_PODL` only and does not support C33 status, power class, power limits, voltage/current telemetry, or IRQ notifications.

Risks and test signals: risks are regulator exclusivity conflicts, cached admin state drifting if external regulator users modify state, lack of classification/status detail, and single-line assumptions from default `nr_lines`. Test signals include probe deferral for missing regulator, initial enabled/disabled state reporting, enable/disable idempotence through ethtool, module unload with devm cleanup, and behavior when regulator operations fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/pse_regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/si3474.c -->
# sources/distributed-fs/ceph-client/drivers/net/pse-pd/si3474.c

Purpose: implements an I2C PSE controller driver for the Skyworks Si3474. It models the two internal four-channel quads as one logical PSE controller, supports only 4-pair PSE configurations, and routes operations to the primary or ancillary I2C address based on channel number.

Important APIs and functions: `si3474_i2c_probe()` validates device IDs on both quad addresses, creates the secondary ancillary I2C client, and registers the PSE controller. `si3474_setup_pi_matrix()` and `si3474_get_of_channels()` map PSE PI pairset nodes to hardware channel numbers. Runtime callbacks include `si3474_pi_enable()`, `si3474_pi_disable()`, `si3474_pi_get_admin_state()`, `si3474_pi_get_pw_status()`, `si3474_pi_get_voltage()`, and `si3474_pi_get_actual_pw()`.

Control flow: probe runs on the primary I2C client, reads vendor/chip/firmware registers, creates the secondary client at `addr + 1`, validates that device ID too, then registers eight possible lines with PSE core. Matrix setup requires each described PI to have two pairsets; each pairset node provides a `reg` channel number. Enable clears shutdown bits in `PORT_MODE_REG` for both channels and writes `DETECT_CLASS_ENABLE_REG`; disable clears the same mode bits. Voltage and power reads choose enabled channels and sum currents for both 4-pair channels.

State and persistence: `struct si3474_priv` stores two I2C clients, embedded `pse_controller_dev`, OF node, and `si3474_pi_desc` channel mapping with 4-pair flags. Hardware state lives in quad registers for port mode, detect/class enable, power status, VPWR/channel voltage, and channel current. There is no firmware update or IRQ state in this driver.

Dependencies and integration: depends on I2C SMBus operations, ancillary I2C device creation, OF pairset descriptions parsed by PSE core, and PSE core C33 ethtool/regulator integration. It advertises `ETHTOOL_PSE_C33`.

Risks and test signals: risks include unsupported 2-pair DT configurations, channel-number boundary checks, pairsets spanning quads while only one client is selected from the first channel, lack of IRQ/event reporting, and register bit-mask mistakes between channel index and upper status bits. Test signals include primary/secondary ID validation, DT matrix with four 4-pair PIs, enable/disable on channels 0-3 and 4-7, voltage zero when not powered, actual power summing both channels, and failure cleanup of the ancillary I2C client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/si3474.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/tps23881.c -->
# sources/distributed-fs/ceph-client/drivers/net/pse-pd/tps23881.c

Purpose: implements an I2C PSE controller driver for TI TPS23881/TPS23881B PoE PSE controllers. It supports Clause 33 PSE operations, device-tree port matrix remapping, software power-budget control through the PSE core, power measurement and limits, class-derived power requests, optional SRAM firmware loading, reset GPIO, and interrupt-driven notifications.

Important APIs and functions: PSE callbacks include `tps23881_pi_enable()`, `tps23881_pi_disable()`, admin/power status getters, voltage/current/actual-power helpers, power-class and power-limit get/set/range callbacks, and `tps23881_pi_get_pw_req()`. Matrix setup is handled by `tps23881_setup_pi_matrix()`, `tps23881_match_port_matrix()`, `tps23881_sort_port_matrix()`, `tps23881_write_port_matrix()`, and `tps23881_set_ports_conf()`. Firmware helpers `tps23881_flash_sram_fw_part()` and `tps23881_flash_sram_fw()` load parity/SRAM blobs for TPS23881. IRQ mapping flows through `tps23881_irq_handler()` and event-specific helpers for over-temperature, over-current, disconnection, detection, and classification.

Control flow: probe validates I2C, match data, optional reset GPIO timing, device ID, optional SRAM firmware load, firmware revision, and 16-bit access mode. It then registers a C33 PSE controller with static budget evaluation and configures IRQ support. Matrix setup parses `channels` nodes, matches PSE pairsets, enforces non-overlap and 4-pair grouping within a four-port bank, sorts logical channels to hardware-required consecutive layout, writes `PORT_MAP`, semiauto mode, disconnect/detect/class registers, and port power allocation. IRQ handling reads interrupt masks/registers until the pin clears and fills PSE notification bitmaps for the core.

State and persistence: `struct tps23881_priv` stores the I2C client, embedded `pse_controller_dev`, OF node, and per-port channel mapping, 4-pair flag, existence flag, and cached manual power-policy byte. Hardware state includes op mode, port map, power enable/off commands, detection/classification enable, disconnect enable, power limit registers, SRAM firmware, and interrupt masks/events.

Dependencies and integration: depends on I2C SMBus word/byte access, firmware loader for older model SRAM images, GPIO reset, OF topology, PSE core IRQ helper and static power-budget behavior, ethtool C33 status/events, and regulator budget APIs indirectly through the core.

Risks and test signals: risks include firmware blob absence on TPS23881, safe-mode detection, reset timing, endian/register layout errors in 16-bit SMBus words, loss of power-limit registers after PWOFF or overcurrent, matrix sorting for mixed 2-pair/4-pair ports, IRQ storms if events do not clear within retry count, and returning class-table `-ERANGE` through budget control. Test signals include probe for both compatible strings, firmware-load success/failure, default and DT remapped matrices, 2-pair and 4-pair enable/disable, power-limit set and persistence after disable/overcurrent, class request values, IRQ detection/classification/disconnection/thermal/current notifications, and static budget behavior under over-budget conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/pse-pd/tps23881.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/rionet.c -->
# sources/distributed-fs/ceph-client/drivers/net/rionet.c

Purpose: implements Ethernet-over-RapidIO using RapidIO messaging and doorbells. It creates one Ethernet netdevice per RapidIO master port/net, discovers capable peers, exchanges join/leave doorbells, and transmits Ethernet frames over outbound message mailboxes.

Important APIs and functions: `rionet_add_dev()` discovers RapidIO devices, creates the netdevice on first capable local net, and adds capable remote peers. `rionet_setup_netdev()` allocates the active peer table, sets a deterministic RapidIO-derived MAC address, registers netdev ops, and registers the device. `rionet_open()` requests inbound doorbells and inbound/outbound mailboxes, fills RX buffers, starts the queue, and sends join doorbells. `rionet_start_xmit()` maps multicast to all active peers or unicast to the destination ID encoded in the MAC. `rionet_inb_msg_event()`, `rionet_outb_msg_event()`, and `rionet_dbell_event()` service RX, TX completion, and peer membership changes. Removal and shutdown paths send leave doorbells and release resources.

Control flow: late init registers a reboot notifier, class interface for local mport removal, and RapidIO bus subsys interface for device add/remove. When a capable RapidIO device appears, the driver initializes the per-net `nets[id]` state and peer list. Opening the netdev allocates hardware messaging resources and broadcasts join; incoming join marks peers active and replies with join; leave clears active slots. TX queues SKBs into RapidIO outbound messages and frees them on outbound completion events.

State and persistence: global `nets[RIONET_MAX_NETS]` holds netdevice pointers, peer lists, spinlocks, active peer arrays, and active counts. `struct rionet_private` holds RX/TX SKB rings, slots/counters, locks, message verbosity, mport, and open flag. Peer state stores `rio_dev` and outbound doorbell resource. State is memory-only and tied to RapidIO topology and netdevice lifetime.

Dependencies and integration: depends on RapidIO core, message mailbox and doorbell APIs, netdevice/ethernet helpers, ethtool, reboot notifier, class/subsys interfaces, and configured TX/RX ring sizes. It uses RapidIO source/destination capability registers and route-entry sizing.

Risks and test signals: risks include peer active-table bounds by destid, SKB reference handling for multicast fanout, RX buffer ownership after `rio_get_inb_message()`, TX completion slot accounting, ring sizes assumed power-of-two by masking, resource cleanup if open partially fails, and races between peer removal and transmit. Test signals include mport add/remove, capable/incapable peer discovery, open/close resource allocation, join/leave doorbell exchange, unicast and multicast traffic, remote removal while packets queue, reboot notifier leave behavior, ethtool driver info/message level, MTU bounds, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/rionet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/slip/Kconfig

Purpose: defines configuration for the SLIP serial-line network driver and related optional modes.

Important options: `SLIP` is a tristate depending on `TTY` and builds the core serial line IP driver. `SLHC` is a hidden tristate for Van Jacobsen TCP/IP header compression helpers. `SLIP_COMPRESSED` depends on `SLIP` and selects `SLHC` to enable CSLIP compressed headers. `SLIP_SMART` enables keepalive and line-fill support. `SLIP_MODE_SLIP6` enables six-bit SLIP encapsulation for links that cannot pass full 8-bit data.

Control flow: the compression, smart keepalive, and SLIP6 options are visible only inside `if SLIP`. Enabling compressed SLIP automatically selects the helper module used by the driver. The Makefile uses `CONFIG_SLIP` and `CONFIG_SLHC` to include the actual objects.

State and persistence: no runtime state is defined here. Symbol choices determine which code paths and module objects are present in the kernel build.

Dependencies and integration: connects the SLIP networking driver to the TTY subsystem and compression helper object. Help text documents operational expectations and legacy use cases such as SLiRP and poor serial links.

Risks and test signals: risks are hidden-helper mismatch if compressed mode does not select `SLHC`, unmet TTY dependencies, and untested legacy mode combinations. Test signals include builds for SLIP as module/built-in, compressed mode selecting `slhc.o`, smart and SLIP6 option compilation, and disabled SLIP hiding optional features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/slip/Makefile

Purpose: maps SLIP-related Kconfig symbols to Kbuild objects.

Important build rules: `CONFIG_SLIP` builds `slip.o`; `CONFIG_SLHC` builds `slhc.o`.

Control flow: Kbuild includes the core SLIP network driver when selected and includes Van Jacobsen header compression helpers when `SLHC` is selected directly or via `SLIP_COMPRESSED`. The helper is separate so compression support can be modularized with users that need it.

State and persistence: no runtime state is defined. The file only controls object inclusion.

Dependencies and integration: integrates with `drivers/net/slip/Kconfig` and the parent networking Makefile. `slip.o` consumes exported symbols from `slhc.o` when compressed SLIP support is enabled.

Risks and test signals: risks are unresolved symbols if Kconfig selection and object inclusion diverge, or stale object names after source changes. Test signals include `CONFIG_SLIP=m/y`, `CONFIG_SLIP_COMPRESSED=y` selecting `CONFIG_SLHC`, standalone `SLHC` module builds, and clean modpost output for compressed and uncompressed configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/slhc.c -->
# sources/distributed-fs/ceph-client/drivers/net/slip/slhc.c

Purpose: implements Van Jacobsen TCP/IP header compression helpers used by CSLIP and related serial-line protocols. It compresses repetitive IPv4/TCP headers into compact deltas, reconstructs compressed packets on receive, and maintains per-direction connection-state slots.

Important APIs and functions: exported functions are `slhc_init()`, `slhc_free()`, `slhc_compress()`, `slhc_uncompress()`, `slhc_remember()`, and `slhc_toss()`. `slhc_init()` allocates receive/transmit `struct cstate` arrays and initializes transmit LRU order. `slhc_compress()` validates IPv4/TCP ACK packets, locates or allocates a transmit state, encodes deltas for sequence, ACK, window, urgent pointer, IP ID, and special interactive/data cases, or emits an uncompressed TCP packet with a connection ID. `slhc_remember()` records an uncompressed TCP header into receive state. `slhc_uncompress()` applies deltas to the current receive state and rebuilds IP/TCP headers. `encode()`, `decode()`, `put16()`, and `pull16()` implement compact field encoding with bounds checks.

Control flow: transmit callers pass an original packet plus output buffer; non-TCP, fragmented, control, runt, or option-changing packets are sent as regular/uncompressed IP. Compressible packets produce `SL_TYPE_COMPRESSED_TCP` with optional explicit connection ID. Receive callers first process `SL_TYPE_UNCOMPRESSED_TCP` through `slhc_remember()` to seed state, then compressed packets through `slhc_uncompress()`. `SLF_TOSS` forces discard after errors until a packet with explicit state arrives.

State and persistence: `struct slcompress` stores transmit and receive state arrays, current/oldest slot indices, flags, and compression statistics counters. Each `struct cstate` stores previous IP/TCP headers, options, slot ID, LRU link, header size, and initialization state. State is in-memory per line/session and is freed by `slhc_free()`.

Dependencies and integration: active implementation is compiled under `CONFIG_INET`; otherwise stubs log debug messages and fail. It depends on IPv4/TCP header definitions, checksum helpers, unaligned stores, and `net/slhc_vj.h` constants. Symbols are exported for SLIP/CSLIP users.

Risks and test signals: risks include malformed compressed input bounds, state desynchronization after line errors, checksum/header-length validation gaps, option copying limits, unaligned checksum writes, slot-count edge cases including zero slots, and legacy assumptions around IPv4 only. Test signals include allocation/free with 0/1/255 slots, TCP option and IP option packets falling back to uncompressed, compressed ACK/data special cases, corrupted compressed packets setting `SLF_TOSS`, uncompressed packets reseeding state, checksum failure accounting, non-INET stub builds, and round-trip compression/decompression against known VJ traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/slip/slhc.c -->

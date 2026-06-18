# subset-b-004520 Prestera driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_devlink.c

Purpose: Implements Prestera devlink integration: switch allocation/registration, physical devlink ports, firmware version reporting, devlink traps/groups, packet trap reporting, and devlink drop counters.

Important APIs/types/functions: `prestera_devlink_alloc/free/register/unregister()`, `prestera_devlink_port_register/unregister()`, `prestera_devlink_traps_register/unregister()`, `prestera_devlink_trap_report()`. Internal `struct prestera_trap` maps a devlink trap to a firmware CPU code; `struct prestera_trap_item` stores action and devlink trap context; `struct prestera_trap_data` is hung off `sw->trap_data`.

Control flow: switch setup allocates `struct prestera_switch` as devlink private data, registers trap groups, then registers each trap from `prestera_trap_items_arr`. Devlink calls `prestera_trap_init()` to bind trap contexts. RX code reports trapped packets by CPU code through `prestera_devlink_trap_report()`, which looks up the trap item and calls `devlink_trap_report()` with the ingress devlink port. `trap_drop_counter_get` converts the devlink trap back to its CPU code and queries firmware counters via `prestera_hw_cpu_code_counters_get()`.

State and persistence: State is runtime-only: devlink object lifetime, per-port `struct devlink_port`, allocated `sw->trap_data`, trap context pointers, and initial actions. There is no persistent storage. Trap actions cannot be changed because `prestera_trap_action_set()` returns `-EOPNOTSUPP`.

Dependencies/integration: Depends on `net/devlink.h`, Prestera switch/port structures, and `prestera_hw` CPU-code counter commands. Integrated from `prestera_main.c` during switch and port creation, and from RX/TX handling when CPU-tagged packets are reported.

Risks: The trap table must stay synchronized with firmware CPU code assignments and devlink documentation. Unknown CPU codes are silently ignored in trap reporting. Error unwind during registration must mirror partial trap/group registration exactly. Counter support assumes the firmware maps all driver trap CPU codes to requested counter types.

Test signals: Build warnings around devlink API compatibility, `devlink trap show`, per-trap packet reports, `devlink trap stats`, firmware version from `devlink dev info`, port registration visibility, and injection of CPU-trapped packets for representative CPU codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_devlink.h

Purpose: Declares the devlink-facing Prestera lifecycle, port registration, and trap reporting API used by the rest of the driver.

Important APIs/types/functions: Exports prototypes for switch devlink allocation/free/register/unregister, devlink port register/unregister, trap register/unregister, and `prestera_devlink_trap_report()`. Includes `prestera.h` for switch, port, device, and skb-adjacent type visibility.

Control flow: This header is consumed by switch setup/teardown in `prestera_main.c`, packet receive paths that report traps, and the devlink implementation itself. It does not define state or inline behavior.

State and persistence: No direct state. It exposes functions that operate on `struct prestera_switch`, `struct prestera_device`, `struct prestera_port`, and `struct sk_buff` owned elsewhere.

Dependencies/integration: Couples `prestera_main.c` to the devlink module while hiding trap table internals. Also provides the public hook used by RX/TX code to translate firmware CPU code metadata into devlink trap notifications.

Risks: Prototype drift against `prestera_devlink.c` would break builds. Because it includes the broad `prestera.h`, changes in central structures can ripple into all include users.

Test signals: Compile coverage is the primary signal. Runtime signals are successful switch probe, devlink port registration, trap registration, and trapped packet reports through call sites declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_dsa.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_dsa.c

Purpose: Encodes and decodes Prestera 16-byte DSA tags used to move packets between host CPU and switch firmware/hardware.

Important APIs/types/functions: `prestera_dsa_parse()` parses big-endian four-word DSA buffers into `struct prestera_dsa`; `prestera_dsa_build()` creates a FROM_CPU tag from destination device and port fields. Bit layouts are expressed with `GENMASK`, `BIT`, `FIELD_GET`, and `FIELD_PREP`.

Control flow: RX parsing converts four network-order words, rejects non-TO_CPU commands and missing extension bits, reconstructs VID, hardware device number, source port, VLAN metadata, and CPU code. TX building fills FROM_CPU command, split device fields, destination eport, required extension bits, and writes network-order words.

State and persistence: Stateless transformation of caller-provided buffers and structs. No allocation and no retained state.

Dependencies/integration: Used by Prestera RX/TX paths to strip or prepend proprietary tags. Depends on Linux bitfield helpers and the public structures in `prestera_dsa.h`.

Risks: Bitfield layout is firmware/hardware ABI-sensitive. Parsing casts an unaligned `u8 *` buffer to `__be32 *`, so platform alignment assumptions matter. Build path does not currently encode VLAN fields, so callers must understand tag limitations.

Test signals: Packet RX from multiple ports/devices with CPU codes, TX to specific eports, VLAN-tagged trap parsing, malformed DSA command rejection, extension-bit rejection, and endian validation on non-little-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_dsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_dsa.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_dsa.h

Purpose: Defines the public Prestera DSA tag contract shared by RX/TX code.

Important APIs/types/functions: `PRESTERA_DSA_HLEN` fixes tag length at 16 bytes. `enum prestera_dsa_cmd` defines TO_CPU and FROM_CPU command values. `struct prestera_dsa_vlan` carries VID, priority, CFI, and tagged status. `struct prestera_dsa` carries VLAN metadata, hardware device number, port number, and CPU code. Declares parse/build functions.

Control flow: Consumers allocate/populate `struct prestera_dsa`, then call parse for ingress tags or build for egress tags. The header has no inline control flow.

State and persistence: No state. It defines transient packet metadata only.

Dependencies/integration: Included by the DSA implementation and packet datapath. The CPU code field integrates with devlink trap reporting and hardware trap metadata.

Risks: The tag length and struct interpretation must match the firmware/hardware DSA format. Any enum or field expansion must preserve existing ABI expectations in parser/build logic.

Test signals: Compile-time users in RX/TX, packet round-trip tests, and assertions that callers reserve/consume exactly `PRESTERA_DSA_HLEN` bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_dsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_ethtool.c

Purpose: Implements ethtool operations for Prestera netdevs: driver info, link settings, advertised/supported modes, port type, MDIX, FEC, statistics names/values, link status, and autoneg restart.

Important APIs/types/functions: Exports `prestera_ethtool_ops`. Internal mapping tables translate Prestera link modes, FEC modes, and port types to ethtool bitsets. Key functions include `prestera_ethtool_get_link_ksettings()`, `prestera_ethtool_set_link_ksettings()`, `prestera_ethtool_get_fecparam()`, `prestera_ethtool_set_fecparam()`, stats string/count/get helpers, and `prestera_ethtool_nway_reset()`.

Control flow: Get link settings either delegates to phylink or composes supported/advertising/lp-advertising from cached port capabilities and firmware reads. Set link settings validates port type and MDIX, converts ethtool advertising to Prestera bitmaps, then chooses autoneg or forced speed/duplex configuration. FEC get reads active firmware MAC mode; FEC set requires autoneg off and rewrites cached MAC configuration through `prestera_port_cfg_mac_write()`.

State and persistence: Uses runtime port state: `caps`, `autoneg`, advertised link modes/FEC, `cfg_phy`, `cfg_mac`, cached MAC/PHY state, and cached hardware stats. Settings are pushed to firmware but not persisted by the driver beyond in-memory port structures.

Dependencies/integration: Depends on `prestera_hw` port PHY/MAC/stat calls, `prestera_main.c` config helpers, phylink for SFP-backed ports, and Linux ethtool core. Stats mirror `struct prestera_port_stats` layout using offset-based macros.

Risks: Mapping tables must stay aligned with firmware enums and ethtool bit definitions. Forced type/speed selection can reject valid combinations if caps are stale. FEC changes while autoneg is on are explicitly blocked. Cached stats may lag hardware by the delayed stats worker.

Test signals: `ethtool -i`, `ethtool <dev>`, advertised mode changes, autoneg on/off transitions, MDIX on copper ports, SFP phylink delegation, `ethtool --show-fec/--set-fec`, stats string count matching struct fields, and link mode tests across copper/fibre/direct-attach port types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_ethtool.h

Purpose: Declares the Prestera ethtool operations table for netdev setup.

Important APIs/types/functions: Provides `extern const struct ethtool_ops prestera_ethtool_ops;` and forward declarations for Prestera port/event types.

Control flow: `prestera_main.c` assigns this table to each created netdev. The actual callbacks live in `prestera_ethtool.c`.

State and persistence: No direct state. It exposes an immutable ops table.

Dependencies/integration: Includes `<linux/ethtool.h>`. Used by port creation to connect ethtool user requests to firmware-backed port operations.

Risks: Header is intentionally small; drift between the extern declaration and implementation would be caught at build/link time.

Test signals: Compile/link success and `netdev->ethtool_ops` behavior on registered Prestera ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flow.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flow.c

Purpose: Provides the tc block setup dispatcher for Prestera hardware offload, binding shared flow blocks to ports and routing flower/matchall classifier operations to their implementations.

Important APIs/types/functions: Public `prestera_flow_block_setup()`. Internal `prestera_flow_block_cb()` dispatches `TC_SETUP_CLSFLOWER` to flower and `TC_SETUP_CLSMATCHALL` to matchall. `prestera_flow_block_get/put/create/destroy`, `prestera_flow_block_bind/unbind`, and `prestera_setup_flow_block_clsact()` manage flow block callback references and port bindings.

Control flow: On `FLOW_BLOCK_BIND`, the driver looks up or allocates a shared `flow_block_cb`, allocates a port binding, optionally binds existing ACL ruleset zero to the port, registers the callback with tc, and records the block on ingress or egress port state. On unbind it destroys matchall state, removes the port binding, unbinds ACL rulesets, drops callback references, and clears the port pointer.

State and persistence: Runtime state lives in `struct prestera_flow_block`: binding list, template list, ruleset pointer, block callback, matchall priority bounds, rule count, net namespace, switch, and ingress flag. A global `prestera_block_cb_list` tracks registered callbacks for tc.

Dependencies/integration: Depends on Linux flow block APIs, Prestera ACL, flower, matchall, and span modules. Called from `ndo_setup_tc` in `prestera_main.c`.

Risks: Shared block reference counting must be exact across multiple ports. `prestera_setup_flow_block_unbind()` calls `prestera_mall_destroy()` for the whole block, so matchall state is block-wide rather than per-port. Error paths must avoid leaking bindings or callback refs. ACL ruleset binding must be consistent when a block is already offloaded.

Test signals: `tc qdisc add clsact`, flower and matchall add/delete/stats, shared block bound to multiple ports, ingress and egress blocks, unbind cleanup, and error injection around ACL bind failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flow.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flow.h

Purpose: Defines the shared tc flow block data structures and setup entry point.

Important APIs/types/functions: `struct prestera_flow_block_binding` stores a port, list node, and SPAN id. `struct prestera_flow_block` stores bindings, switch/net pointers, ACL ruleset, tc block callback, flower template list, matchall priority state, rule count, and direction. Declares `prestera_flow_block_setup()`.

Control flow: No inline behavior. The structures are populated in `prestera_flow.c` and consumed by flower/matchall/span/ACL code.

State and persistence: All fields are runtime-only and tied to tc block lifetime. No persistent storage.

Dependencies/integration: Includes `<net/flow_offload.h>` and forward-declares Prestera switch/port types. It is the contract connecting netdev tc setup with classifier-specific modules.

Risks: This struct is shared across multiple feature modules; changing field semantics can affect ACL binding, SPAN mirror rules, and template cleanup. Direction (`ingress`) drives ACL client selection and matchall priority constraints.

Test signals: Build coverage across flow, flower, matchall, and span modules; runtime block bind/unbind with multiple ports and both directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flower.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flower.c

Purpose: Translates tc flower rules and templates into Prestera ACL rulesets, key/mask fields, hardware actions, counters, and statistics.

Important APIs/types/functions: `prestera_flower_replace()`, `prestera_flower_destroy()`, `prestera_flower_stats()`, `prestera_flower_tmplt_create/destroy()`, `prestera_flower_template_cleanup()`, and `prestera_flower_prio_get()`. Internal parsing handles metadata, control, basic L2/L3/L4 fields, VLAN, ICMP, port ranges, and actions.

Control flow: Replace first checks priority compatibility with matchall, gets or creates a ruleset for the chain, creates an ACL rule keyed by cookie, parses matches/actions into `rule->re_key`/`rule->re_arg`, offloads the ruleset if needed, then adds the rule to hardware. Destroy looks up by chain/cookie and removes hardware and software state. Stats resolve the rule and update tc delayed hardware stats. Template creation parses a rule-shaped template, fixes PCL id keymask, preserves the keymask on a ruleset, attempts offload, and stores a ruleset reference in the block template list.

State and persistence: Rules, rulesets, jump ruleset references, counters, policers, and templates are runtime kernel/firmware state. Template list entries keep ruleset refs until template destroy or block cleanup.

Dependencies/integration: Depends on Linux flow dissector/action APIs, Prestera ACL, flow block state, and matchall priority helpers. `FLOW_ACTION_GOTO` uses chain rulesets; delayed stats use ACL counters.

Risks: Only specific dissector keys and actions are supported; unsupported flags/actions return extack errors. IPv6 address match key is allowed in the mask check but parsing only explicitly handles IPv4 address payloads in this file. Multiple actions of the same kind are rejected. GOTO can only jump to a higher chain. Priority interaction with matchall differs by ingress/egress direction and can reject rule ordering.

Test signals: Flower add/delete for supported keys, unsupported key/action extack messages, GOTO chain forward-only behavior, police/count/trap/drop/accept actions, delayed stats updates, templates with later rule insertion, priority conflict tests with matchall, and cleanup after block unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flower.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flower.h

Purpose: Declares the tc flower offload API used by the generic flow block dispatcher and matchall priority coordination.

Important APIs/types/functions: Prototypes for replace, destroy, stats, template create/destroy/cleanup, and `prestera_flower_prio_get()`.

Control flow: `prestera_flow.c` dispatches tc flower commands to these functions. `prestera_matchall.c` uses `prestera_flower_prio_get()` to prevent unsupported ordering between mirror matchall and flower ACL rules.

State and persistence: No direct state; functions operate on `struct prestera_flow_block` and tc offload objects.

Dependencies/integration: Includes `<net/pkt_cls.h>` for tc classifier structs and forward-declares the flow block.

Risks: Header API is small but central to classifier dispatch; signature drift affects flow and matchall modules.

Test signals: Compile/link coverage and tc flower command routing through `prestera_flow_block_setup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_flower.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_hw.c

Purpose: Implements the main firmware command ABI for Prestera switch functionality and event parsing. It is the central hardware abstraction used by switch setup, ports, VLAN/FDB, bridge, ACL/vTCAM, counters, SPAN, router, LAG, policer, RX/TX, flood-domain, and MDB code.

Important APIs/types/functions: Command enum `prestera_cmd_type_t`, many packed firmware request/response structs, `prestera_hw_build_tests()` ABI size assertions, command wrappers `prestera_cmd_ret[_wait]()`/`prestera_cmd()`, event parsers and handler registry, plus exported `prestera_hw_*` functions declared in `prestera_hw.h`.

Control flow: Public helpers fill little-endian firmware messages, call `prestera_cmd*()` through `sw->dev->send_req`, validate ACK/status in `__prestera_cmd_ret()`, and decode response fields. Switch init initializes the event handler list, performs firmware switch init, installs RX message callbacks, and stores switch capabilities. Firmware event receive decodes event type/id, parses port/FDB payloads, finds a registered handler under RCU, and invokes it.

State and persistence: Maintains runtime firmware-facing switch attributes (`port_count`, MTU limits, switch id, LAG limits, nexthop table size), event handler list, and hardware object IDs returned by firmware (bridges, vTCAMs, rules, counters, SPAN IDs, RIFs, VRs, nexthop groups, flood domains). No durable persistence beyond firmware state and in-memory driver structures.

Dependencies/integration: Depends on `prestera_device->send_req` supplied by PCI transport, central Prestera structs, ACL action definitions, router HW types, counter stats, netdev/LAG helpers, and Linux endian/ethernet helpers. It is called by nearly every higher-level Prestera module.

Risks: This file is firmware ABI-sensitive: struct sizes, endian conversions, command IDs, and response lengths must match firmware. `prestera_hw_nhgrp_blk_get()` uses a static response buffer, which is not reentrant. Dynamic message sizing for vTCAM rules/counters/flood ports must match firmware expectations. Event handler lookup supports one handler per event type and uses RCU copying semantics. Several helpers return generic `-EINVAL` for firmware failure, limiting diagnostics.

Test signals: Build-time `BUILD_BUG_ON` layout checks, full probe/switch init, firmware command timeout/failure injection, port config/stat operations, VLAN/FDB/bridge operations, ACL rule add/delete with multiple actions, counter block read/trigger/clear, router LPM/NH/RIF/VR operations, SPAN/mirror, LAG membership and FDB, flood-domain/MDB programming, and port/FDB event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_hw.h

Purpose: Defines the public firmware/hardware API surface and shared enums for the Prestera driver.

Important APIs/types/functions: Contains enums for accept frame type, FDB flush modes, MAC/link modes, port types/transceivers/FEC/duplex, STP states, policer types, CPU-code counter type, vTCAM direction, and counter clients. Declares all `prestera_hw_*` switch, port, VLAN, FDB, bridge, vTCAM, counter, SPAN, router, VR/LPM/NH, event, RX/TX, LAG, trap counter, policer, flood-domain, and MDB APIs.

Control flow: No implementation. Higher layers call these APIs; `prestera_hw.c` implements firmware message transport and decoding.

State and persistence: No direct state. The declarations operate on `prestera_switch`, `prestera_port`, and hardware object structures owned elsewhere.

Dependencies/integration: Includes `prestera_acl.h` for ACL action/match contracts and forward-declares many shared structures. This header is the integration boundary between feature modules and firmware commands.

Risks: Enum numeric values are ABI-facing and must remain aligned with firmware and ethtool mappings. Broad inclusion can amplify rebuilds and coupling. API changes affect many driver subsystems.

Test signals: Kernel compile coverage, ABI layout checks in `prestera_hw.c`, and subsystem tests for every declared hardware API family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_main.c

Purpose: Core Prestera switch/netdev driver lifecycle. It registers devices from transport drivers, initializes switch subsystems, creates netdev ports, handles link events, LAG/upper-device notifications, multicast flood-domain objects, workqueues, and module lifecycle.

Important APIs/types/functions: Exported `prestera_device_register/unregister()`, workqueue helpers, port lookup helpers, port config helpers, LAG helpers, flood-domain/MDB helpers, and netdev identity helpers. Netdev ops implement open/stop/xmit/setup_tc/change_mtu/get_stats64/set_mac_address. Switch lifecycle is `prestera_switch_init/fini()`; port lifecycle is `prestera_port_create/destroy()`.

Control flow: Transport calls `prestera_device_register()`, which allocates devlink private switch state and runs switch init. Switch init initializes hardware, base MAC, netdevice notifier, router, switchdev, RX/TX, event handlers, counters, ACL, SPAN, devlink traps, LAG table, ports, then registers devlink. Port creation allocates an etherdev, reads firmware port IDs/caps, registers devlink port, sets MTU/MAC/MAC/PHY config, initializes RX/TX port state, registers netdev, and binds SFP phylink where device tree describes it. Teardown reverses setup.

State and persistence: Maintains switch port list under rwlock, base MAC, LAG table, OF node, per-port cached config/state/stats, delayed stat workers, phylink state, VLAN list, and pointers to ingress/egress flow blocks. State is runtime and firmware-backed, not persisted across module reload.

Dependencies/integration: Integrates almost every Prestera subsystem: hardware, ACL, flow, SPAN, RX/TX, devlink, ethtool, counter, switchdev, router, phylink, netdevice notifier, bridge, VLAN, and LAG kernel APIs.

Risks: Initialization and unwind ordering is critical because subsystems depend on earlier hardware and notifier setup. `prestera_lag_create()` tests `if (lag)` after a loop where `lag` will be non-NULL even when no free entry is found, so full-table handling depends on surrounding logic. Port SFP bind returns `err` even when no matching node is found; correctness relies on prior initialization along all loop paths. Link event code reads `port->state_mac.oper` after cache write instead of local `smac.oper`, relying on immediate cache consistency.

Test signals: PCI probe through device registration, all init error-injection unwind paths, netdev register/unregister, port open/close for copper and SFP/phylink, link up/down events and carrier changes, delayed stats, MTU/MAC validation, tc setup, bridge/LAG/VLAN upper device notifier behavior, multicast MDB flood-domain programming, and module load/unload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_matchall.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_matchall.c

Purpose: Implements tc matchall offload for Prestera mirroring/SPAN rules.

Important APIs/types/functions: `prestera_mall_replace()`, `prestera_mall_destroy()`, and `prestera_mall_prio_get()`. Internal helpers check priority compatibility with flower rules and maintain matchall priority min/max on a flow block.

Control flow: Replace requires exactly one action, a Prestera target port, chain 0/offload eligibility, `FLOW_ACTION_MIRRED`, and `ETH_P_ALL`. It checks ordering against existing flower priorities, then adds a SPAN rule for each port binding in the block. On partial failure it rolls back already added SPAN rules. Destroy removes SPAN rules from all bindings and resets priority state.

State and persistence: Uses `block->mall` to track whether matchall is bound and the min/max priority. SPAN IDs live in each flow block binding and are managed by the SPAN subsystem. No persistent storage.

Dependencies/integration: Depends on flow block binding state, flower priority query, SPAN rule add/delete, Prestera netdev validation, and tc matchall structures.

Risks: Only singular mirred mirror-like actions are supported. Shared block behavior means destroy removes SPAN for every binding. Priority ordering differs for ingress/egress and can be surprising to users mixing flower and matchall. Rollback must align with list traversal after failures.

Test signals: `tc filter add matchall ... action mirred`, invalid action count, non-Prestera target rejection, chain/offload rejection, ingress/egress priority conflicts with flower, multi-port shared block mirroring, duplicate SPAN handling, and destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_matchall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_matchall.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_matchall.h

Purpose: Declares the matchall/SPAN offload API used by the flow dispatcher and flower priority checks.

Important APIs/types/functions: Prototypes for matchall replace/destroy and `prestera_mall_prio_get()`.

Control flow: `prestera_flow.c` dispatches `TC_SETUP_CLSMATCHALL` commands here; `prestera_flower.c` consults matchall priority bounds through this header.

State and persistence: No direct state; functions mutate `struct prestera_flow_block` state.

Dependencies/integration: Includes `<net/pkt_cls.h>` and forward-declares `struct prestera_flow_block`.

Risks: API signature changes must be coordinated with flow and flower modules.

Test signals: Compile/link coverage and matchall tc command execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_matchall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_pci.c

Purpose: PCI transport and firmware loader for Prestera devices. It maps BARs, downloads firmware through loader registers, initializes firmware command/event queues, handles MSI interrupts, and registers the core Prestera device.

Important APIs/types/functions: PCI probe/remove, firmware loader structs/register offsets, `struct prestera_fw`, event queue helpers, command queue send path, `prestera_fw_init/uninit/load()`, firmware version/header parsing, IRQ handler, and `prestera_fw_send_req()` implementing `prestera_device->send_req`.

Control flow: Probe enables PCI, requests BARs, sets DMA mask, maps control and packet-processor regions, allocates `prestera_fw`, loads firmware if loader is ready, waits for FW ready, discovers command/event queue locations, allocates event buffer, creates event workqueue, enables MSI, requests IRQ, then calls `prestera_device_register()`. Command sending serializes by queue mutex, writes request to IO memory, signals firmware, waits for reply, bounds-checks reply length, copies response, and acknowledges. IRQ handles RX status for packets and schedules event queue drain work.

State and persistence: Runtime state includes mapped IO addresses, firmware image pointer during load, loader ring indexes, command/event queue descriptors, event message buffer, workqueue, PCI device data, firmware revision, and core `prestera_device`. Firmware binary is requested and released during load; no persistent driver storage.

Dependencies/integration: Depends on Linux PCI, firmware loader, MSI IRQ, IO polling, circular buffer helpers, and the core Prestera registration API in `prestera_main.c`. Firmware paths vary for selected ARM64-based device IDs and fall back from supported version 4.1 to 4.0.

Risks: Firmware ABI and register offsets are critical. Loader send writes 32-bit chunks from firmware data and assumes safe alignment/length handling. Queue counts from firmware are trusted against fixed arrays. Event work disables/enables event control around draining; missed ordering could affect event delivery. Command queue `qid` is not range-checked in `prestera_fw_send_req()`. Fallback firmware may lack newer features expected elsewhere.

Test signals: PCI ID matching, BAR layout on AC3X/Aldrin/AC5X variants, firmware request/fallback/header/version/CRC paths, loader timeout/status errors, FW ready timeout, command timeout/oversize reply, MSI event and packet interrupts, event queue wraparound, module remove cleanup, and core switch registration after firmware ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router.c

Purpose: Bridges Linux IPv4 routing/neighbour state into Prestera router hardware objects. It maintains kernel FIB/neighbour caches, reacts to route/address/neighbour notifications, programs hardware RIF/FIB/nexthop state through `prestera_router_hw`, and updates kernel offload/trap flags.

Important APIs/types/functions: Public `prestera_router_init/fini()`. Internal cache types `prestera_kern_neigh_cache` and `prestera_kern_fib_cache`, rhashtable params, route/neighbour conversion helpers, arbiter functions `prestera_k_arb_fib_evt()`, `prestera_k_arb_n_evt()`, `__prestera_k_arb_fc_apply()`, `__prestera_k_arb_nc_apply()`, RIF address notifier handlers, FIB and netevent work handlers, and periodic neighbour hardware-state probing.

Control flow: Init allocates router state, initializes router hardware library, two rhashtables, nexthop hardware-state cache, delayed neighbour probe work, inetaddr validators/notifiers, netevent notifier, and FIB notifier. IPv4 address up/down creates or destroys RIF entries for standalone Prestera ports. FIB notifications are copied under RCU into work items, then processed under RTNL to create/update/remove FIB cache entries and corresponding hardware FIB nodes. Neighbour updates create/fetch neighbour cache entries, read kernel neighbour validity/MAC/interface, update neighbour LPM and hardware nexthop state, and update kernel offload flags.

State and persistence: Runtime-only router state includes rhashtable caches, held `fib_info` refs, held net_device refs for neighbours/RIFs, RIF entries, nexthop groups/neighbours, FIB nodes, hardware nexthop bitmap cache, notifier registrations, and delayed work. Hardware state is recreated from kernel events after driver init; no durable persistence.

Dependencies/integration: Depends on Linux FIB, ARP/neighbour, inetaddr, netevent, switchdev, l3mdev, VLAN/macvlan/LAG/bridge device helpers, rhashtable, Prestera core netdev identity helpers, and `prestera_router_hw` object APIs. Uses shared workqueues from `prestera_main.c`.

Risks: IPv6 helpers exist partially but notifier path ignores non-AF_INET; IPv6 support is incomplete. Route overlap handling is a TODO limited to local/main table interactions. ECMP is capped by `PRESTERA_NHGR_SIZE_MAX` and larger groups silently avoid nexthop cache creation. Several helper failures return 0 in cache creation paths, reducing visibility. Correctness depends on RTNL/RCU/refcount discipline across async work. Fini destroys FIB cache rhashtable after `prestera_k_arb_abort()` already frees it, so double-destroy behavior should be reviewed against rhashtable API expectations.

Test signals: IPv4 address add/del RIF programming, invalid MAC or multicast address rejection, route add/replace/delete for unicast/direct/trap/drop cases, local/main overlap cases, neighbour reachable/stale/dead transitions, kernel offload/trap flags, ECMP up to four nexthops, unsupported ECMP >4, nexthop hardware-state polling, driver unload with pending works, notifier unregister ordering, and route/neighbour churn under RTNL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_router.c -->

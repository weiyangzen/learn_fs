# Research: subset-b-004330

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_static_config.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_static_config.c

Purpose: this file is the SJA1105/SJA1110 static-configuration serializer and validator. It translates the driver's in-memory table model into the packed block format consumed by the switch over SPI, including per-table headers, CRCs, device IDs, sparse block-ID mapping, chip-generation compatibility matrices, and table memory management helpers.

Important APIs, types, and functions: `sja1105_pack()`, `sja1105_unpack()`, and `sja1105_packing()` wrap the generic packing API with the SJA1105 little-word-first layout. `sja1105_crc32()` calculates the Ethernet CRC used by table headers and payloads. Each `*_entry_packing()` routine maps one logical structure from `sja1105_static_config.h` onto exact hardware bit positions, with separate layouts for E/T, P/Q/R/S, and SJA1110 variants. `sja1105_static_config_check_valid()`, `sja1105_static_config_pack()`, `sja1105_static_config_get_length()`, `sja1105_static_config_init()`, `sja1105_static_config_free()`, `sja1105_table_delete_entry()`, and `sja1105_table_resize()` are the exported service layer.

Control flow: callers initialize a `struct sja1105_static_config` with one of the exported table-ops arrays, populate `config->tables`, validate mandatory and conditional blocks, allocate a byte buffer using `sja1105_static_config_get_length()`, then call `sja1105_static_config_pack()`. Packing writes the device ID, iterates all populated block indices, emits a CRC-protected table header, packs every entry through the table's `ops->packing` callback, writes a table data CRC, and terminates with a zero-length final header whose CRC is later replaced during config upload.

State and persistence: the file persists no hardware state itself. It owns heap allocations for table entries inside `struct sja1105_static_config`, and these tables become the authoritative static configuration that other SJA1105 code reloads into the switch. `sja1105_static_config_free()` frees populated tables; resize/delete mutate table contents in place and must not be used while callers keep stale entry pointers.

Dependencies and integration points: it depends on `linux/packing.h`, CRC32, slab allocation, and the table/type declarations in `sja1105_static_config.h`. TAS, virtual links, VLAN, FDB, policing, MAC configuration, XMII setup, retagging, AVB, CBS, and SJA1110 PCP remapping all meet here through table entries and chip-specific `sja1105_table_ops` arrays.

Risks: bit positions are hardware-contract code and regressions are silent until a switch rejects or misapplies a static config. Validation is intentionally structural, not semantic; it checks missing tables, TT/VL companion tables, and shared frame-memory overcommit but does not prove forwarding policy correctness. `sja1105_table_delete_entry()` only rejects `i > entry_count`, so callers must avoid passing `i == entry_count`. `sja1105_table_resize()` allocates even for zero length and returns `-ENOMEM` if `kcalloc(0, ...)` produces NULL on a platform. CRC/endian mistakes or wrong ops-array selection affect every config reload.

Test signals: useful tests are pack/unpack round trips for each chip generation, known-good binary static-config images, CRC verification for headers and payloads, validation errors for missing L2/VLAN/MAC/XMII/TT/VL tables, frame-memory accounting with retagging and VL partitions, SJA1110 extended port counts, and live `sja1105_static_config_reload()` success after TAS/VL/VLAN mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_static_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_static_config.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_static_config.h

Purpose: this header defines the SJA1105/SJA1110 static-configuration ABI used by the DSA driver. It names all hardware block IDs, driver block indices, packed entry sizes, maximum entry counts, frame-memory limits, device/part IDs, SJA1110 address helpers, table entry structures, validation results, and serializer function prototypes.

Important APIs, types, and functions: `enum sja1105_blk_idx` is the driver's dense index over sparse hardware block IDs. `struct sja1105_table_ops`, `struct sja1105_table`, and `struct sja1105_static_config` are the central abstractions: each table carries chip-specific packing metadata plus its current entry array. Entry types include schedule, schedule parameters, VL lookup/policing/forwarding, VLAN lookup, L2 lookup/forwarding/policing, general parameters, MAC config, retagging, CBS, XMII params, and SJA1110 PCP remapping. The header exports all chip ops arrays and common packing helpers used by static and dynamic config code.

Control flow: platform identification code selects an ops array such as `sja1105e_table_ops`, `sja1105q_table_ops`, or `sja1110_table_ops`; `sja1105_static_config_init()` binds those ops to every table. Higher-level driver code then allocates entries according to the max counts and table sizes, mutates fields using the typed structures, validates, and asks the C file to pack the result.

State and persistence: the header does not create state, but it fixes the shape of persistent driver state. `struct sja1105_static_config` stores the device ID and all populated tables. Several software-only fields are deliberately embedded next to hardware fields, for example `flow_cookie` in `struct sja1105_vl_lookup_entry`, so packing callbacks must only serialize true hardware members.

Dependencies and integration points: the declarations integrate SJA1105 static config with Linux packing helpers, TAS (`BLK_IDX_SCHEDULE*`), virtual links (`BLK_IDX_VL_*`), DSA VLAN/FDB paths, SJA1110 ACU/CGU/RGU address calculation, and runtime dynamic-config code that reuses common entry packers.

Risks: constants in this header encode hard hardware limits and layouts. Wrong packed sizes, max counts, block ordering, or SJA1110 port-count assumptions can corrupt config images across multiple source files. Since the same structures model multiple chip generations, fields marked "P/Q/R/S only" or "SJA1110 only" must only be acted on by the matching packing routine. Software-only fields must remain excluded from hardware serialization.

Test signals: compile coverage across all `CONFIG_NET_DSA_SJA1105*` variants, static assertions or round-trip tests for packed sizes, table limit boundary tests, SJA1110 11-port configurations, and live driver tests that exercise VLAN, FDB, TAS, VL, XMII, and retagging paths against the same shared table definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_static_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_tas.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_tas.c

Purpose: this file implements Time-Aware Shaper support for SJA1105 using the tc-taprio offload API and the switch's static schedule tables. It merges per-port taprio schedules and global virtual-link gate schedules into the hardware's linear schedule table, coordinates schedule start/stop with the PTP clock, and rejects configurations that the hardware scheduler cannot safely execute.

Important APIs, types, and functions: `sja1105_setup_tc_taprio()` is the DSA tc entry point. `sja1105_init_scheduling()` rebuilds `BLK_IDX_SCHEDULE`, schedule entry points, schedule params, and entry-point params. `sja1105_tas_set_runtime_params()` computes enabled state, earliest/latest base times, and maximum cycle time. `sja1105_tas_check_conflicts()` and `sja1105_gating_check_conflicts()` protect against simultaneous gate events and incompatible cycle periods. The workqueue state machine uses `sja1105_tas_adjust_drift()`, `sja1105_tas_set_base_time()`, `sja1105_tas_start()`, `sja1105_tas_stop()`, and `sja1105_tas_check_running()`.

Control flow: replacing a taprio schedule validates command type, rejects cycle-time extension, verifies every interval is representable in 200 ns hardware deltas, checks conflicts against other port schedules and tc-gate VL schedules, stores a refcounted offload, rebuilds static scheduling tables, and calls `sja1105_static_config_reload(..., SJA1105_SCHEDULING)`. Destroying taprio frees the saved offload, rebuilds, and reloads. The state machine starts TAS only after an `ADJUSTFREQ` event, writes correction period and PTPSCHTM, starts the hardware engine, polls whether it reached running state, and stops/restarts after PTP clock steps.

State and persistence: persistent runtime state lives in `priv->tas_data`: per-port taprio offloads, global `gating_cfg`, work item, TAS state, last PTP operation, earliest and operational base times, max cycle time, and enabled flag. Hardware state is static schedule-table contents plus PTP command registers (`ptpstrtsch`, `ptpstopsch`, `PTPSCHTM`, `PTPCLKCORP`). Teardown cancels work and frees saved offloads.

Dependencies and integration points: it depends on the SJA1105 static-config layer, PTP helpers, DSA switch state, `tc_taprio_qopt_offload`, tc-gate generated `gating_cfg` from the VL file, and time conversion helpers such as `ns_to_sja1105_delta()`.

Risks: the hardware cannot tolerate simultaneous gate events, so conflict detection is critical and assumes existing saved schedules are already mutually valid. Base times for all schedules must be close enough to fit `SJA1105_TAS_MAX_DELTA`; otherwise reload is rejected. The scheduler is coupled to PTP frequency adjustment and cannot survive clock steps without restart. The code comments note that switch reset is required for admin-to-oper transition, so Linux's seamless taprio model is only partially matched. Error handling after storing a new offload can leave software state changed if later scheduling build fails.

Test signals: configure/destroy taprio per port, attempt conflicting base times and intervals, mix taprio and tc-gate rules, step and slew the PTP clock, verify static schedule tables after reload, check `ptpstrtsch`/`ptpstopsch` state, observe traffic gate timing at 200 ns multiples, and run boundary tests around zero, maximum interval, and non-multiple cycle periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_tas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_tas.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_tas.h

Purpose: this header defines the SJA1105 TAS feature boundary. It exposes the taprio offload API, TAS setup/teardown hooks, PTP adjustment notifications, gate-conflict checking, and scheduling-table rebuild entry point when `CONFIG_NET_DSA_SJA1105_TAS` is enabled, and provides stubs otherwise.

Important APIs, types, and functions: `SJA1105_TAS_MAX_DELTA` is the maximum representable hardware interval in scheduler deltas. `enum sja1105_tas_state` models disabled, enabled-not-running, and running hardware states. `enum sja1105_ptp_op` records whether the last PTP operation was none, a clock step, or an adjustfreq. `struct sja1105_gate_entry` and `struct sja1105_gating_config` hold the global tc-gate schedule consumed by TAS. `struct sja1105_tas_data` is embedded in `struct sja1105_private` and carries all TAS runtime state.

Control flow: callers invoke `sja1105_tas_setup()` during switch setup, use `sja1105_setup_tc_taprio()` for taprio replace/destroy, call `sja1105_tas_clockstep()` or `sja1105_tas_adjfreq()` from PTP clock operations, and call `sja1105_tas_teardown()` on removal. The VL file calls `sja1105_gating_check_conflicts()` and `sja1105_init_scheduling()` when tc-gate rules change.

State and persistence: the enabled build persists offload pointers, gate lists, state-machine work, base times, and max cycle time. The disabled build intentionally reduces `struct sja1105_tas_data` to a dummy byte so the private structure remains valid without TAS code.

Dependencies and integration points: it includes `<net/pkt_sched.h>` for taprio types and relies on DSA, SJA1105 private state, PTP callbacks, and optional VL support. The stubs preserve linkability for builds without TAS while making taprio return `-EOPNOTSUPP`.

Risks: the disabled stub for `sja1105_gating_check_conflicts()` has a signature that differs from the enabled declaration in this snapshot, which is only harmless if no disabled-build caller type-checks that path. Consumers must honor the config guard because `struct sja1105_tas_data` layout changes substantially. Gate entries point at `struct sja1105_rule`, so rule lifetime must exceed schedule rebuild and teardown.

Test signals: build with TAS enabled and disabled, exercise taprio callbacks, verify PTP notifications schedule work only when needed, delete VL/taprio rules without dangling gate entries, and check that disabled builds reject offload cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_tas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_vl.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_vl.c

Purpose: this file implements SJA1105 virtual-link offload for tc flower redirect/trap/drop-like routing and tc-gate time-triggered flows. It programs the switch's VL lookup, policing, forwarding, and forwarding-parameters tables, composes global gate schedules for time-triggered VLs, and exposes hardware error counters through flow stats.

Important APIs, types, and functions: `sja1105_vl_redirect()` creates or updates non-critical VL routing rules. `sja1105_vl_gate()` creates time-triggered critical VLs from tc-gate actions. `sja1105_vl_delete()` removes a port from a VL rule and rebuilds dependent state. `sja1105_vl_stats()` reads per-VL status counters. Internal helpers include `sja1105_compose_gating_subschedule()`, `sja1105_insert_gate_entry()`, `sja1105_gating_cfg_time_to_interval()`, `sja1105_init_virtual_links()`, `sja1105_vl_key_lower()`, and `sja1105_find_vlid()`.

Control flow: redirect validates whether the port is VLAN-aware or VLAN-unaware and whether the key shape matches, creates a `SJA1105_RULE_VL` rule if needed, updates the ingress port mask and destination mask, then rebuilds virtual-link tables. Gate offload validates cycle-time extension, 200 ns base/cycle/interval granularity, nonzero and bounded intervals, lack of `IntervalOctetMax`, and a single IPV per VL. It stores gate entries, composes a global gating subschedule, rebuilds VL tables, and rejects conflicts against taprio. Delete updates the rule list, recomposes gating, rebuilds VL and schedule tables, and reloads static config with `SJA1105_VIRTUAL_LINKS`.

State and persistence: persistent software state is the `priv->flow_block.rules` list plus per-rule VL fields such as destination ports, sharindx, base/cycle times, gate entries, IPV, maxlen, and previous stats. Hardware state is held indirectly in static-config VL tables and schedule tables. For VLAN-unaware ports, lookup entries use the DSA tag_8021q VID derived from standalone or bridge context.

Dependencies and integration points: the file integrates tc flower/gate action data, DSA VLAN filtering, DSA tag_8021q, `sja1105_static_config_reload()`, TAS scheduling, SPI register reads for VL status, and `sja1105_frame_memory_partitioning()`.

Risks: VL lookup entries must be sorted by MAC, VLAN ID, port, and PCP; an ordering regression changes hardware matching. Critical VLs require companion policing/forwarding tables and share frame memory with L2 forwarding. The FIXME around tag_8021q bridge VID updates means bridge changes can invalidate VLAN-unaware VL keys. The code only implements time-triggered critical VL table population in detail; other critical modes need careful extension. Gate rule allocation and rule-list mutation must unwind cleanly on later validation failures to avoid stale rules or leaked `vl.entries`.

Test signals: tc flower redirect in VLAN-aware and VLAN-unaware modes, multiple ingress ports per rule, sorted lookup table inspection, tc-gate schedules with valid and invalid 200 ns multiples, conflicts with taprio and other gate events, static-config reload success, VL status counter increments for timing/length/unreleased errors, bridge membership changes affecting tag_8021q VID, and deletion of the last port from a VL rule.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_vl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_vl.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_vl.h

Purpose: this header exposes the optional SJA1105 virtual-link offload API to the rest of the SJA1105 driver. It declares redirect, delete, gate, and stats helpers when `CONFIG_NET_DSA_SJA1105_VL` is enabled and returns extack-backed `-EOPNOTSUPP` stubs otherwise.

Important APIs, types, and functions: `sja1105_vl_redirect()` handles routing-style VL actions, `sja1105_vl_delete()` removes a rule from a port, `sja1105_vl_gate()` accepts tc-gate timing data and creates time-triggered VL state, and `sja1105_vl_stats()` reports hardware drop/error counters through `flow_stats`. Parameters include `struct sja1105_private`, ingress port, rule cookie, `struct sja1105_key`, destination port mask, gate index, priority, base/cycle time, and action gate entries.

Control flow: flow-block parsing code in the main SJA1105 driver can call these helpers without open-coding config guards. Enabled helpers mutate rule/static-config state and may trigger scheduling rebuilds; disabled helpers only set "Virtual Links not compiled in" in `netlink_ext_ack`.

State and persistence: this header does not own state. It defines the API that mutates `priv->flow_block.rules`, `priv->static_config`, and `priv->tas_data.gating_cfg` in the C implementation.

Dependencies and integration points: it includes `sja1105.h`, which supplies private driver state, rule/key types, DSA context, and flow stats types. It is used by tc flower/gate offload paths and by removal/reload logic.

Risks: callers must treat the enabled helpers as transactional only to the extent implemented by `sja1105_vl.c`; failures can occur after partial rule creation and need correct unwinding. The disabled stubs make feature absence visible to user space but still compile callers, so tests need both config variants.

Test signals: build with VL enabled and disabled, verify extack messages for disabled builds, exercise all four helper calls from tc offload paths, and ensure rule deletion and stats collection behave consistently after config reloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_vl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-core.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-core.c

Purpose: this is the transport-independent DSA core for Vitesse/Microchip VSC7385, VSC7388, VSC7395, and VSC7398 switches. It detects and resets the chip, initializes switching memory and ports, registers DSA operations, manages VLAN and dsa_8021q behavior, drives the internal MDIO bus, handles phylink MAC state, exposes ethtool counters, manages FDB entries, and registers a 4-line GPIO controller.

Important APIs, types, and functions: exported entry points are `vsc73xx_is_addr_valid()`, `vsc73xx_probe()`, `vsc73xx_remove()`, and `vsc73xx_shutdown()`. Core helpers include `vsc73xx_read/write/update_bits()`, `vsc73xx_detect()`, `vsc73xx_setup()`, `vsc73xx_init_port()`, `vsc73xx_reset_port()`, internal PHY read/write callbacks, VLAN table read/write/update helpers, bridge VLAN software-list helpers, FDB hash/read/add/delete/dump helpers, phylink callbacks, and GPIO callbacks. `vsc73xx_ds_ops` wires these into DSA.

Control flow: bus frontends allocate and fill `struct vsc73xx`, then call `vsc73xx_probe()`. Probe optionally toggles reset, detects chip ID and iCPU boot state, initializes the FDB mutex and random pause-frame MAC, allocates `dsa_switch`, registers it, then registers GPIOs. DSA setup issues a global reset, runs the documented memory-init sequence, clears MAC/VLAN tables, configures buffer mode, holds ports in reset, applies CPU RGMII delay from DT, configures masks, releases internal PHY reset, clears all VLAN table entries, initializes the VLAN list, and registers dsa_8021q tagging.

State and persistence: `struct vsc73xx` persists chip ID, reset GPIO, DSA switch, pause MAC address, bus ops, per-port PVID/tag_8021q state, bridge VLAN list, and FDB lock. Hardware state includes analyzer masks, VLAN and MAC tables, MAC config per port, RGMII delays, internal MDIO registers, counters, and GPIO bits. Remove unregisters DSA and asserts reset; shutdown calls `dsa_switch_shutdown()`.

Dependencies and integration points: it depends on DSA, dsa_8021q tagging, switchdev bridge/VLAN/FDB callbacks, phylink, phylib internal MDIO access, GPIO, OF properties for RGMII delays, random MAC generation, and transport ops from SPI/platform files.

Risks: the setup path contains magic memory-init sequencing and port reset ordering from datasheets. Address validation intentionally excludes nonexistent ports, especially the port-5 hole on 5+1 chips. VLAN handling works around tag_8021q and hardware limitations that allow only none, one, or all egress-untagged VLANs per port. FDB rows have four buckets and can return `-EOVERFLOW`. Polling timeouts on MDIO, VLAN, MAC table, or arbiter operations indicate hardware lockups. The CPU-port tag protocol is dsa_8021q because the internal frame header is unavailable in this operating mode.

Test signals: probe/reset on all four chip IDs, iCPU boot-state rejection, dsa_8021q registration, port enable/link-up/down at 10/100/1000, RGMII delay DT values, VLAN add/delete/filtering transitions including PVID and untagged constraints, FDB add/delete/dump including dsa_8021q VID hiding, STP forwarding masks, MTU changes to jumbo sizes, internal PHY MDIO access, ethtool stats reads, GPIO get/set/direction operations, and remove/reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-platform.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-platform.c

Purpose: this file is the platform/MMIO bus frontend for the VSC73xx DSA core. It supports switches attached to a CPU address bus and translates the core's block/subblock/register accesses into big-endian memory-mapped I/O operations.

Important APIs, types, and functions: `struct vsc73xx_platform` stores the platform device, MMIO base, and embedded `struct vsc73xx`. `vsc73xx_make_addr()` encodes block, subblock, and register into the platform address layout. `vsc73xx_platform_read()` and `vsc73xx_platform_write()` implement `struct vsc73xx_ops`. Probe/remove/shutdown bridge the platform driver to `vsc73xx_probe()`, `vsc73xx_remove()`, and `vsc73xx_shutdown()`.

Control flow: probe allocates state with devm, stores drvdata, initializes the embedded core object with device pointer, private pointer, and ops, maps resource 0 with `devm_platform_ioremap_resource()`, and calls the common probe. Remove and shutdown fetch drvdata and delegate to the common core, with shutdown also clearing platform drvdata.

State and persistence: persistent state is only the mapped base address and embedded core state. Register accesses are synchronous and not explicitly locked here; higher layers or the bus ordering provide serialization as needed. Devm owns allocation and mapping lifetimes.

Dependencies and integration points: it depends on platform-driver APIs, OF matching for `vitesse,vsc7385`, `vitesse,vsc7388`, `vitesse,vsc7395`, and `vitesse,vsc7398`, and the shared VSC73xx core ops contract. The hardware is documented as running big-endian by default, so it uses `ioread32be()` and `iowrite32be()`.

Risks: address encoding masks block/subblock fields; invalid block/subblock combinations are rejected by the core helper but invalid register numbers are not separately range-checked. Incorrect endianness or DT resource size will make chip detection fail or corrupt registers. There is no transport-specific locking, so future asynchronous users would need care.

Test signals: platform probe with valid MMIO resource, chip-ID read through big-endian access, common DSA registration, invalid-address rejection, remove/shutdown delegation, and DT compatible coverage for all four switch models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-spi.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-spi.c

Purpose: this file is the SPI bus frontend for the VSC73xx DSA core. It serializes 32-bit switch register reads and writes into the device's SPI command format and delegates all switch behavior to `vitesse-vsc73xx-core.c`.

Important APIs, types, and functions: `struct vsc73xx_spi` stores the `spi_device`, a mutex protecting SPI traffic, and the embedded core object. `vsc73xx_make_addr()` encodes read/write mode, block, and subblock into the SPI command byte. `vsc73xx_spi_read()` builds a two-transfer message with a 4-byte command and 4-byte receive buffer. `vsc73xx_spi_write()` builds a two-transfer write with a 2-byte command and 4-byte big-endian data payload. `vsc73xx_spi_probe()`, remove, and shutdown wrap the common core lifecycle.

Control flow: probe allocates state, takes a device reference with `spi_dev_get()`, initializes core fields and the SPI mutex, forces SPI mode 0 and 8 bits per word, calls `spi_setup()`, then calls `vsc73xx_probe()`. Each register access validates block/subblock, performs `spi_sync()` under the mutex, and converts values manually between byte arrays and `u32`.

State and persistence: transport state is the SPI device pointer and mutex; common switch state is embedded in `vsc73xx_spi.vsc`. Register caching is not present. Remove unregisters the common switch but does not explicitly drop the `spi_dev_get()` reference in this snapshot, so lifetime management should be reviewed against SPI core expectations.

Dependencies and integration points: it depends on Linux SPI APIs, OF and SPI ID tables for all supported VSC73xx models, and the shared `struct vsc73xx_ops` interface. It exports no switch logic itself.

Risks: SPI command format, mode, and byte order must match the hardware exactly. A missing explicit `spi_dev_put()` after `spi_dev_get()` may be a reference leak unless balanced elsewhere. Because every access is synchronous and mutex-protected, slow SPI buses can stretch DSA operations and polling loops. Invalid register numbers beyond block/subblock validation are not rejected here.

Test signals: SPI probe with `spi_setup()` success, chip-ID detection over SPI, concurrent register operations serialized by the mutex, read/write byte-order tests with known registers, remove/shutdown behavior, and compatibility matching through both OF and SPI ID tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx.h

Purpose: this header defines the shared state and bus abstraction for the Vitesse VSC73xx DSA drivers. It lets SPI and platform frontends provide register I/O while the common core owns switch behavior.

Important APIs, types, and functions: `VSC73XX_MAX_NUM_PORTS` fixes the DSA allocation at eight ports to cover 5+1 and 8-port chips while tolerating the invalid port-5 hole. `struct vsc73xx_portinfo` stores per-port PVID state for bridge VLAN filtering and tag_8021q modes. `struct vsc73xx` is the central core object with device, reset GPIO, DSA switch, GPIO chip, chip ID, control-frame MAC, ops, transport private pointer, per-port state, bridge VLAN list, and FDB lock. `struct vsc73xx_ops` provides `read` and `write` callbacks. `struct vsc73xx_bridge_vlan` mirrors bridge VLAN membership and untagged state in software.

Control flow: bus drivers allocate an object containing `struct vsc73xx`, fill `dev`, `priv`, and `ops`, then call `vsc73xx_probe()`. The core later calls transport `read`/`write` for every register operation and provides `vsc73xx_remove()`/`vsc73xx_shutdown()` for frontend teardown.

State and persistence: this header defines all long-lived common driver state but allocates none. The VLAN list is explicitly software-maintained because hardware VLAN state alone is insufficient to compute tag/untag/PVID transitions.

Dependencies and integration points: it includes Linux device, ethernet, and GPIO declarations and is shared by `vitesse-vsc73xx-core.c`, `vitesse-vsc73xx-platform.c`, and `vitesse-vsc73xx-spi.c`.

Risks: transport implementers must honor the `vsc73xx_ops` contract, including the core's block/subblock validity rules and 32-bit register semantics. The fixed eight-port representation means callers must consistently avoid invalid ports. Software VLAN mirror correctness is required for later hardware commits.

Test signals: compile all frontends, probe through both transport paths, validate portinfo transitions under tag_8021q and bridge VLAN filtering, confirm invalid ports are ignored by DSA operations, and exercise remove/shutdown using the shared declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/Kconfig

Purpose: this Kconfig fragment declares build options for Arrow SpeedChips XRS7003/XRS7004 DSA support and its transport frontends.

Important APIs, types, and functions: `NET_DSA_XRS700X` is the hidden core tristate selected by transport drivers; it depends on `NET_DSA`, selects `NET_DSA_TAG_XRS700X`, and selects `REGMAP`. `NET_DSA_XRS700X_I2C` is the user-visible I2C transport option, depends on `NET_DSA && I2C`, selects the core, and selects `REGMAP_I2C`. `NET_DSA_XRS700X_MDIO` is the user-visible MDIO transport option, depends on `NET_DSA`, and selects the core.

Control flow: users choose a transport; Kconfig pulls in the shared core and the required tagging/regmap infrastructure. The Makefile then builds `xrs700x.o` for the core and the selected transport object.

State and persistence: Kconfig persists only build-time selection state. Runtime state is in the C files.

Dependencies and integration points: this integrates the driver with DSA, the XRS700x tagger, regmap, I2C, and the MDIO frontend listed in the Makefile but outside this work item.

Risks: the core symbol is not user-selectable, so missing transport selection yields no driver. MDIO does not explicitly select a named regmap bus helper here, so its source must provide or depend on the needed regmap support. Incorrect selects can produce link failures or a DSA driver without its tag protocol.

Test signals: `olddefconfig`/`menuconfig` coverage for I2C-only, MDIO-only, both transports, and disabled DSA; module dependency checks showing the tagger and regmap objects are built; and runtime probe with each selected transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/Makefile

Purpose: this Makefile maps XRS700x Kconfig symbols to the objects built by kbuild.

Important APIs, types, and functions: `obj-$(CONFIG_NET_DSA_XRS700X) += xrs700x.o` builds the common DSA core, `obj-$(CONFIG_NET_DSA_XRS700X_I2C) += xrs700x_i2c.o` builds the I2C frontend, and `obj-$(CONFIG_NET_DSA_XRS700X_MDIO) += xrs700x_mdio.o` builds the MDIO frontend.

Control flow: Kconfig transport selections determine which object files are linked into the kernel or built as modules. The core is selected by each transport and therefore accompanies any frontend.

State and persistence: there is no runtime state; this file only controls build artifacts.

Dependencies and integration points: it relies on the Kconfig symbols in the same directory and on source files that export/import the common core APIs declared by `xrs700x.h`.

Risks: if a transport selects the core as built-in while another is modular, kbuild combinations need to preserve symbol availability. The Makefile references `xrs700x_mdio.o`, so source presence outside this work item is required for MDIO builds.

Test signals: build the driver as built-in and module for I2C, MDIO, and combined configurations, and verify module dependency ordering for `xrs700x`, `xrs700x_i2c`, and `xrs700x_mdio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x.c

Purpose: this is the transport-independent DSA core for Arrow SpeedChips XRS7003/XRS7004 switches. It detects the chip, initializes port state, registers the DSA switch, configures forwarding masks and STP behavior, exposes MIB counters and stats64, handles phylink speed selection, and offloads HSR/PRP redundancy on supported port pairs.

Important APIs, types, and functions: exported objects are `xrs7003e_info`, `xrs7003f_info`, `xrs7004e_info`, `xrs7004f_info`, `xrs700x_switch_alloc()`, `xrs700x_switch_register()`, `xrs700x_switch_remove()`, and `xrs700x_switch_shutdown()`. DSA callbacks in `xrs700x_ops` include setup/teardown, STP state, phylink caps, ethtool strings/stats, stats64, bridge join/leave, and HSR join/leave. Internal helpers cover MIB accumulation, regmap-field setup, reset, BPDU and HSR supervision inbound policy filters, port setup, bridge forwarding masks, HSR/PRP configuration, and chip detection.

Control flow: a transport calls `xrs700x_switch_alloc()`, assigns `priv->regmap`, then calls `xrs700x_switch_register()`. Register reads detect the expected chip ID from OF match data and set `ds->num_ports`; regmap fields are allocated for per-port state bits; per-port MIB buffers are initialized; and DSA is registered. DSA setup resets the switch, disables ports, programs forwarding masks, sets CPU ports to management mode, adds BPDU policy filters on user ports, and starts delayed MIB polling every three seconds.

State and persistence: `struct xrs700x` persists the DSA switch, device, transport private pointer, regmap, regmap fields, delayed MIB work, and per-port data. Each `struct xrs700x_port` keeps accumulated MIB counters, a stats64 snapshot, a mutex, and u64 stats sync state. Hardware state includes port forwarding/management/speed fields, policy filters, forwarding masks, HSR config, and captured counters.

Dependencies and integration points: it depends on DSA, phylink, bridge/STP state, regmap and regmap fields, OF match data, Linux HSR/PRP helpers, ethtool stats, stats64 synchronization, and the XRS700x register definitions/tag protocol.

Risks: counter accumulation assumes periodic reads plus capture semantics; missed or wrapped 32-bit hardware counters can skew stats. HSR/PRP offload is limited to ports 1 and 2 and only HSR v1/PRP v1, with both redundant ports required before enabling hardware redundancy. Bridge forwarding masks use inverted "1 disables forwarding" semantics. BPDU and HSR supervision policy filters are enabled/disabled indirectly through STP and HSR paths. Phylink callbacks are minimal and only program selected speed on link-up.

Test signals: chip-ID detection for each OF compatible, reset polling, DSA registration, STP transitions and BPDU CPU delivery, bridge join/leave forwarding masks, phylink speed changes on RMII/RGMII ports, ethtool and rtnl stats updates over multiple MIB intervals, HSR/PRP join/leave on ports 1 and 2 including feature flags and supervision forwarding, teardown cancelling delayed work, and shutdown via DSA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x.h

Purpose: this header defines the shared data model and exported core lifecycle for XRS700x DSA transport drivers.

Important APIs, types, and functions: `struct xrs700x_info` describes an expected chip ID, name, and port count and is exported for OF match data. `struct xrs700x_port` stores per-port MIB lock, accumulated counter array, stats64 snapshot, and u64 sync primitive. `struct xrs700x` stores the DSA switch, device, transport private pointer, regmap, per-port regmap fields for port state/speed, delayed MIB work, and port array. Public functions allocate, register, remove, and shutdown a switch instance.

Control flow: a bus frontend calls `xrs700x_switch_alloc()`, initializes `priv->regmap`, and then calls `xrs700x_switch_register()`. The core uses the fields declared here to register DSA and later to service callbacks. Remove and shutdown are frontend-facing wrappers.

State and persistence: the header defines all persistent common runtime state but owns no allocations itself. The port array and MIB arrays are allocated by the core after chip detection sets the port count.

Dependencies and integration points: it includes Linux device, mutex, regmap, workqueue, u64 stats, and if_link definitions. It is shared by I2C and other transport frontends plus the common core.

Risks: frontends must set a valid regmap before registration; otherwise detection and regmap-field allocation fail. MIB data is dynamically sized to the static MIB table in the C file, so any table changes must keep allocation and copy sizes synchronized. Transport private data is opaque and must be cast only by the owning frontend.

Test signals: compile all XRS700x transports, allocate/register/remove through each bus, verify per-port MIB allocation for 3- and 4-port variants, and confirm stats synchronization on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_i2c.c

Purpose: this file is the I2C transport frontend for the XRS700x DSA core. It implements the switch's 32-bit register, 16-bit value I2C protocol as a custom regmap bus and delegates switch behavior to `xrs700x.c`.

Important APIs, types, and functions: `struct xrs700x_i2c_cmd` is the packed wire command containing a big-endian 32-bit register and big-endian 16-bit value. `xrs700x_i2c_reg_read()` writes `reg | 1` then receives a 16-bit value. `xrs700x_i2c_reg_write()` sends register and value together. `xrs700x_i2c_regmap_config` defines 32-bit registers, 16-bit values, stride 2, no cache, custom read/write, and big-endian formatting. Probe/remove/shutdown call `xrs700x_switch_alloc()`, `xrs700x_switch_register()`, `xrs700x_switch_remove()`, and `xrs700x_switch_shutdown()`.

Control flow: probe allocates the common switch object, initializes a devm regmap using the custom I2C operations, stores client data, and registers the switch. Remove and shutdown fetch client data and delegate to the common core, with shutdown clearing client data.

State and persistence: transport state is the `i2c_client` pointer passed as core private data and the devm regmap stored in `priv->regmap`. No register cache is used, so all accesses hit the bus.

Dependencies and integration points: it depends on Linux I2C, regmap, OF match data for `arrow,xrs7003e`, `arrow,xrs7003f`, `arrow,xrs7004e`, and `arrow,xrs7004f`, and the common XRS700x core. The match `.data` provides the expected chip info consumed by core detection.

Risks: I2C read/write helpers only treat negative transfer returns as errors; short positive transfers are not rejected. `max_register = 0` with custom callbacks relies on regmap not enforcing a range that would block real addresses. Protocol correctness depends on the `reg | 1` read marker and big-endian conversion. There is no explicit bus lock here beyond I2C core serialization.

Test signals: I2C probe on all compatibles, regmap read/write of known registers, detection ID match/mismatch, short-transfer fault injection, DSA registration through I2C, remove/shutdown delegation, and no-cache behavior for changing hardware counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_i2c.c -->

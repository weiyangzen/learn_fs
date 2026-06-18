# subset-b-006192

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethernet/eth.c -->
# sources/distributed-fs/ceph-client/net/ethernet/eth.c

## Purpose
This file implements generic Ethernet netdevice helpers for the Linux network core. It supplies default Ethernet header operations, default `net_device` setup, Ethernet GRO offload glue, MAC address validation and assignment helpers, and platform/firmware/NVMEM MAC address discovery.

## Important APIs, Types, And Functions
Exported APIs include `eth_header()`, `eth_type_trans()`, `eth_get_headlen()`, `eth_header_parse()`, `eth_header_cache()`, `eth_header_cache_update()`, `eth_header_parse_protocol()`, `eth_prepare_mac_addr_change()`, `eth_commit_mac_addr_change()`, `eth_mac_addr()`, `eth_validate_addr()`, `ether_setup()`, `alloc_etherdev_mqs()`, `sysfs_format_mac()`, `eth_gro_receive()`, `eth_gro_complete()`, `eth_platform_get_mac_address()`, `platform_get_ethdev_address()`, `nvmem_get_mac_address()`, `fwnode_get_mac_address()`, `device_get_mac_address()`, and `device_get_ethdev_address()`. The file also defines `eth_header_ops` and registers `eth_packet_offload` at `fs_initcall()`.

## Control Flow
Transmit header creation pushes an `ethhdr`, fills protocol or length, chooses the source address from either caller input or `dev->dev_addr`, and either copies the destination, zeroes it for loopback/no-ARP devices, or returns `-ETH_HLEN` to request later address resolution. Receive protocol decoding resets the MAC header, pulls the Ethernet header, classifies packet type, handles DSA devices specially, and falls back to 802.2/802.3 heuristics for length-style frames. GRO receive validates common Ethernet headers across candidates, pulls the Ethernet header, then dispatches by protocol to registered packet offloads.

## State, Persistence, And Dependencies
The helpers mutate in-memory `sk_buff`, `hh_cache`, and `net_device` state only. MAC lookup is read-only against firmware properties and NVMEM cells, except wrappers that copy a successful address into `netdev->dev_addr`. Header-cache publication uses `smp_store_release()` for `hh->hh_len`. Dependencies include `netdevice`, ARP/neighbour cache, flow dissector, DSA, GRO, device properties, Open Firmware, NVMEM, and packet offload registration.

## Integration Points
Network drivers use `ether_setup()` and `alloc_etherdev_mqs()` for Ethernet defaults. Neighbour and routing paths use the header ops. Receive paths use `eth_type_trans()`. GRO uses this file through packet-offload registration for transparent Ethernet bridging/tunnel frames. Platform drivers use the MAC-address helpers to source stable hardware addresses from firmware, architecture hooks, or NVMEM.

## Risks
Header helpers assume adequate skb headroom and valid linear header access. Protocol classification preserves compatibility quirks such as IPX-over-802.3 and DSA tag handling, so changes can regress legacy or switch-tagged traffic. MAC changes deliberately do not update hardware filters for most real devices. Firmware MAC lookup must reject all-zero or malformed addresses and must free NVMEM buffers on every path.

## Test Signals
Useful signals include Ethernet transmit header construction tests, receive protocol classification for Ethernet II, 802.2, 802.3, DSA, and short frames, neighbour header-cache concurrency tests, GRO aggregation/flush behavior, invalid/live MAC address change errors, and firmware/NVMEM MAC lookup fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethernet/eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/Makefile -->
# sources/distributed-fs/ceph-client/net/ethtool/Makefile

## Purpose
This Makefile defines how the kernel ethtool support objects are built. It always links the legacy ioctl and shared common implementation, and conditionally links the generic netlink ethtool implementation when `CONFIG_ETHTOOL_NETLINK` is enabled.

## Important APIs, Types, And Functions
There are no C APIs in this file. The important build variables are `obj-y`, `obj-$(CONFIG_ETHTOOL_NETLINK)`, and `ethtool_nl-y`. `ethtool_nl-y` lists the netlink feature objects, including bitsets, link settings, RSS, debug, features, private flags, rings, channels, coalescing, pause, EEE, timestamp info, cable test, tunnels, FEC, EEPROM, module firmware update, CMIS CDB, PSE/PD, PLCA, PHY, timestamp config, and MSE support.

## Control Flow
Kbuild always includes `ioctl.o` and `common.o`. If ethtool netlink is configured, it builds the composite `ethtool_nl.o` object from the listed `ethtool_nl-y` members and links that composite into the networking tree.

## State, Persistence, And Dependencies
The file has no runtime state. Its persistent effect is build graph selection based on kernel configuration. It depends on Kbuild variable semantics and on source/object names staying aligned.

## Integration Points
This file is the build integration point for all `net/ethtool` netlink request handlers. Adding a new ethtool netlink feature requires adding its object to `ethtool_nl-y`; shared code needed by both ioctl and netlink belongs in always-built objects such as `common.o`.

## Risks
Omitting a required object produces link failures or missing feature handlers under `CONFIG_ETHTOOL_NETLINK`. Adding a netlink-only object to `obj-y` could grow builds that do not enable the netlink interface. Renaming source files requires keeping this object list synchronized.

## Test Signals
Build coverage should include configurations with `CONFIG_ETHTOOL_NETLINK=y` and disabled. Link errors, undefined symbols from netlink dispatch tables, or missing message handlers are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/bitset.c -->
# sources/distributed-fs/ceph-client/net/ethtool/bitset.c

## Purpose
This file implements ethtool netlink bitset encoding, decoding, sizing, and update helpers. It supports both compact bitmap attributes and verbose per-bit nested attributes, and bridges the kernel's `unsigned long` bitmap representation with ethtool's `u32` netlink wire format.

## Important APIs, Types, And Functions
Public helpers include `ethnl_bitset_is_compact()`, `ethnl_bitset32_size()`, `ethnl_put_bitset32()`, `ethnl_update_bitset32()`, `ethnl_parse_bitset()`, `ethnl_bitset_size()`, `ethnl_put_bitset()`, and `ethnl_update_bitset()`. Internal helpers handle interval clearing, nonzero checks, value/mask updates, name-to-index lookup, verbose bit parsing, equality checks, and compact sanity validation.

## Control Flow
Output sizing and emission first account for the outer bitset nest and the `SIZE` attribute. Compact mode serializes raw `VALUE` and optional `MASK` arrays, trimming unused high bits in the last word. Verbose mode emits one nested bit per selected bit, optionally including index, name, and value flag. Parsing distinguishes verbose input from compact input. Compact updates validate size and array lengths, reject unsupported high-bit modifications, then apply value/mask bits. Verbose updates parse each named or indexed bit and either patch selected bits or replace the whole bitmap when `NOMASK` is present.

## State, Persistence, And Dependencies
The functions mutate caller-provided bitmaps and set caller-provided modification flags. There is no persistent state. Dependencies are generic netlink attribute parsing, `bitmap` helpers, `ETH_GSTRING_LEN` name arrays, endian-sensitive bitmap layout, and `netlink_ext_ack` diagnostics.

## Integration Points
Most ethtool netlink feature handlers use these helpers for link modes, device features, Wake-on-LAN modes, debug message classes, FEC modes, and other named capability sets. The header `bitset.h` exposes the API to sibling request files.

## Risks
The main risk is wire-format compatibility: compact `u32` arrays must behave identically on little-endian, 32-bit, and 64-bit big-endian systems. Verbose parsing must reject inconsistent index/name pairs and out-of-range indices. `NOMASK` semantics differ from masked updates, so missing clear behavior can accidentally preserve stale bits. Size estimation must match emission or netlink replies can fail with `-EMSGSIZE`.

## Test Signals
Tests should exercise compact and verbose input/output, named and indexed bits, `NOMASK` replacement, masked updates, out-of-range high bits, mismatched names, empty bitsets, non-multiple-of-32 sizes, and big-endian conversion wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/bitset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/bitset.h -->
# sources/distributed-fs/ceph-client/net/ethtool/bitset.h

## Purpose
This header declares the ethtool netlink bitset helper API shared by feature-specific handlers. It standardizes the string-array type used for named bits and caps accepted bitset size.

## Important APIs, Types, And Functions
`ETHNL_MAX_BITSET_SIZE` limits parsed bitset sizes to `S16_MAX`. `ethnl_string_array_t` represents an array of fixed-width ethtool string names. Declared helpers cover compact detection, reply-size calculation, netlink emission, update-in-place for `unsigned long` and `u32` bitmaps, and parsing to value/mask bitmaps.

## Control Flow
The header has no executable flow. Callers include it, pass their current bitmap plus optional mask/name arrays, and rely on `bitset.c` to calculate reply sizes, serialize replies, parse user input, and report whether state changed.

## State, Persistence, And Dependencies
The header owns no state. It depends on Linux ethtool and netlink types, `struct sk_buff`, `struct nlattr`, and `struct netlink_ext_ack`.

## Integration Points
`debug.c`, `eee.c`, `features.c`, `fec.c`, and other ethtool netlink handlers include this header to expose named capability sets through a common ABI. The API preserves a consistent compact/verbose representation across the whole ethtool generic netlink family.

## Risks
Changing prototypes or the max-size constant can break many handlers and userspace ABI assumptions. The `ethnl_string_array_t` fixed-width string convention matters because many kernel ethtool string tables are not ordinary null-terminated dynamic strings.

## Test Signals
Build coverage across all ethtool netlink handlers is the first signal. ABI tests should confirm all users of bitsets still accept compact and verbose forms and still reject malformed oversize payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/bitset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/cabletest.c -->
# sources/distributed-fs/ceph-client/net/ethtool/cabletest.c

## Purpose
This file implements ethtool netlink actions and notification helpers for PHY cable tests and time-domain reflectometry cable tests. It lets userspace start tests and lets PHY drivers stream structured results back through multicast notifications.

## Important APIs, Types, And Functions
Request policies are `ethnl_cable_test_act_policy` and `ethnl_cable_test_tdr_act_policy`. Action handlers are `ethnl_act_cable_test()` and `ethnl_act_cable_test_tdr()`. Exported driver helpers include `ethnl_cable_test_alloc()`, `ethnl_cable_test_free()`, `ethnl_cable_test_finished()`, `ethnl_cable_test_result_with_src()`, `ethnl_cable_test_fault_length_with_src()`, `ethnl_cable_test_amplitude()`, `ethnl_cable_test_pulse()`, and `ethnl_cable_test_step()`.

## Control Flow
The start handlers parse a PHY-aware ethtool header, take `rtnl_lock()` and per-netdev ops locking, resolve the PHY, verify `ethtool_phy_ops` support, call the driver start callback inside `ethnl_ops_begin()`/`ethnl_ops_complete()`, then multicast a started notification. TDR requests additionally parse optional first/last/step/pair config with defaults and bounds. During a running test, driver callbacks allocate a notification skb, append result nests, and finally close and multicast the completed notification.

## State, Persistence, And Dependencies
Transient notification state is stored on `phydev->skb`, `phydev->ehdr`, and `phydev->nest` between allocation and finish/free. There is no durable persistence. Dependencies include PHY core types, `ethtool_phy_ops`, generic netlink multicast helpers, netdevice locking, and `phy_tdr_config`.

## Integration Points
PHY drivers call the exported helpers while implementing `start_cable_test` or `start_cable_test_tdr`. Netlink command registration in `netlink.c` wires userspace actions to these handlers. Results are consumed asynchronously by ethtool userspace through `ETHTOOL_MSG_CABLE_TEST_NTF` and `ETHTOOL_MSG_CABLE_TEST_TDR_NTF`.

## Risks
The asynchronous result buffer is finite (`SZ_16K`), so dense TDR samples can hit `-EMSGSIZE`. Drivers must balance allocation, finish, and free paths or leak/drop notification skb state. TDR validation must prevent invalid distances, zero step, unsupported pairs, and requests beyond the 150 m limit. Lock ordering with RTNL and netdev ops lock must stay consistent with other ethtool paths.

## Test Signals
Useful tests include unsupported PHY callbacks, malformed TDR config, boundary distances, all-pair and single-pair tests, notification allocation failure, oversized result streams, and driver paths that report result, fault length, pulse, amplitude, and step nests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/cabletest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/channels.c -->
# sources/distributed-fs/ceph-client/net/ethtool/channels.c

## Purpose
This file implements the ethtool netlink get/set interface for netdevice channel counts. Channels describe RX, TX, combined, and other queue group counts plus their driver-reported maxima.

## Important APIs, Types, And Functions
The key local types are `channels_req_info` and `channels_reply_data`. Public objects are `ethnl_channels_get_policy`, `ethnl_channels_set_policy`, and `ethnl_channels_request_ops`. Important functions are `channels_prepare_data()`, `channels_reply_size()`, `channels_fill_reply()`, `ethnl_set_channels_validate()`, and `ethnl_set_channels()`.

## Control Flow
GET checks that `get_channels` exists, calls it under ethtool ops bracketing, and emits only groups with nonzero maxima. SET starts from the current channel configuration, applies any supplied count attributes, exits if unchanged, validates each count against its maximum, ensures at least one RX and TX path remain, asks `ethtool_check_max_channel()` whether existing RSS, ntuple, or memory-provider configuration needs higher channel indices, verifies queues being removed are not busy, then calls the driver `set_channels()` callback.

## State, Persistence, And Dependencies
The only persistent effect is through the driver callback, which reconfigures the device's queue/channel state. The file depends on netdev queue busy checks, `ethtool_ops`, shared netlink update helpers, and `common.c` validation helpers.

## Integration Points
`ethnl_channels_request_ops` is registered in the ethtool netlink dispatcher for `ETHTOOL_MSG_CHANNELS_GET`, SET, and notifications. It mirrors legacy ioctl behavior while adding netlink extack messages and queue-busy validation.

## Risks
Reducing channels can invalidate existing RSS indirection tables, ntuple filters, memory-provider queue bindings, or active AF_XDP/leased queues. Drivers can report inconsistent maxima/counts, so validation before `set_channels()` is critical. Omitting notifications or returning the wrong status can leave userspace with stale topology.

## Test Signals
Tests should cover no-op SET, each maximum violation, zero RX/TX rejection, reductions blocked by RSS or ntuple state, queue-busy failures, successful increases/decreases, and GET replies that omit unsupported channel groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/channels.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/cmis.h -->
# sources/distributed-fs/ceph-client/net/ethtool/cmis.h

## Purpose
This header defines the CMIS CDB command data model and function API used by ethtool module firmware flashing. It captures command identifiers, request/reply wire layouts, validation flags, and helper entry points shared between CDB transport and firmware update code.

## Important APIs, Types, And Functions
Important constants include LPL/EPL maximum payload sizes, CDB page/address identifiers, and validation flags `CDB_F_COMPLETION_VALID`, `CDB_F_STATUS_VALID`, and `CDB_F_MODULE_STATE_VALID`. Types include `ethtool_cmis_cdb`, `ethtool_cmis_cdb_cmd_id`, `ethtool_cmis_cdb_request`, `ethtool_cmis_cdb_cmd_args`, `ethtool_cmis_cdb_rpl_hdr`, and `ethtool_cmis_cdb_rpl`. Declared APIs include command composition, completion-flag adjustment, page initialization, CDB init/fini, condition polling, and command execution.

## Control Flow
The header itself has no executable flow. Callers allocate or initialize an `ethtool_cmis_cdb`, compose command args with LPL/EPL payload pointers and validation flags, then execute commands through `ethtool_cmis_cdb_execute_cmd()`.

## State, Persistence, And Dependencies
The central state is the in-memory `ethtool_cmis_cdb` object, which records CMIS revision, allowable read/write length extension, and max completion time for subsequent commands. Request objects contain a copied LPL payload and optionally point at external EPL storage. Dependencies include ethtool module EEPROM access types and netdevice/module firmware notification types.

## Integration Points
`cmis_cdb.c` implements the API. `cmis_fw_update.c` uses it to run CMIS firmware management commands. Module update orchestration in sibling files passes firmware flash parameters and notification handles into these helpers.

## Risks
The structs intentionally mirror CMIS wire layouts; padding, endianness, and checksum coverage are security- and interoperability-sensitive. EPL payload pointers are not owned by the request struct and must remain valid during command execution. Validation flags vary by CMIS revision, so callers must set them carefully.

## Test Signals
Build and ABI tests should verify struct field offsets, command IDs, checksum coverage, LPL/EPL length limits, revision-dependent flags, and firmware update paths that exercise each declared API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/cmis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/cmis_cdb.c -->
# sources/distributed-fs/ceph-client/net/ethtool/cmis_cdb.c

## Purpose
This file implements the CMIS CDB transport layer used by ethtool module firmware flashing. It discovers CMIS capabilities, validates optional module passwords, composes and writes CDB commands into module EEPROM pages, polls completion/status/module state fields, copies replies, and reports detailed failure strings.

## Important APIs, Types, And Functions
Public APIs are `ethtool_cmis_get_max_lpl_size()`, `ethtool_cmis_cdb_compose_args()`, `ethtool_cmis_page_init()`, `ethtool_cmis_cdb_check_completion_flag()`, `ethtool_cmis_cdb_init()`, `ethtool_cmis_cdb_fini()`, `ethtool_cmis_wait_for_cond()`, and `ethtool_cmis_cdb_execute_cmd()`. Internal helpers read revision and advertisement bytes, validate password, query module features, poll module bytes, wait for completion/status, process replies, write command pieces, write EPL payload pages, and calculate checksums.

## Control Flow
Initialization allocates `ethtool_cmis_cdb`, reads CMIS revision, rejects revisions below 4, checks CDB advertisement support, optionally writes the password and runs Query Status, then queries module features for max completion time. Command execution computes the checksum over the request fields before EPL, rejects overlong LPL, writes the request body to page `0x9f`, writes EPL data page-by-page if present, writes the command ID last to trigger execution, waits for completion and status according to flags, then reads and validates the reply header/payload when a reply is expected.

## State, Persistence, And Dependencies
Persistent module state changes occur through `set_module_eeprom_by_page()` writes into CMIS command and EPL pages; in-kernel state is limited to the allocated CDB context and command args. Polling uses jiffies, sleeps, and module EEPROM reads. Dependencies include driver `get_module_eeprom_by_page`/`set_module_eeprom_by_page`, netlink extack logging, CMIS constants from `cmis.h`, and module firmware notification helpers.

## Integration Points
`cmis_fw_update.c` builds firmware management commands on top of this transport. `module.c` reaches the firmware update flow, and the device's ethtool ops perform the actual module EEPROM I/O. Error messages are routed to firmware flash notifications and netdev logs.

## Risks
This path writes to optical module management memory, so bad offsets, lengths, checksum coverage, or trigger ordering can brick or confuse modules. Polling must avoid endless waits and must handle vendors that require pre-reply sleeps. Reply validation only checks expected length bounds and nonzero check code, so malformed modules remain a risk. EPL paging loops must stay within `0xa0..0xaf` and offsets `128..255`.

## Test Signals
Tests should simulate CMIS revision rejection, missing advertisement support, password failure, LPL length overflow, EPL multi-page writes, timeout vs status failure messages, reply length/check-code failures, and successful CDB commands with and without replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/cmis_cdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/cmis_fw_update.c -->
# sources/distributed-fs/ceph-client/net/ethtool/cmis_fw_update.c

## Purpose
This file implements the CMIS module firmware update sequence over the CDB transport. It queries firmware management capabilities, starts a download, writes firmware blocks by LPL or EPL mechanism, completes the download, runs the new image, reinitializes CDB state, commits the image, resets the module, and emits progress/error/completion notifications.

## Important APIs, Types, And Functions
The exported entry point is `ethtool_cmis_fw_update()`. Internal types include `cmis_fw_update_fw_mng_features`, `cmis_cdb_fw_mng_features_rpl`, `cmis_cdb_fw_write_mechanism`, `cmis_cdb_start_fw_download_pl`, `cmis_cdb_write_fw_block_lpl_pl`, `cmis_cdb_write_fw_block_epl_pl`, and `cmis_cdb_run_fw_image_pl`. Important helpers include feature query, start, LPL write, EPL write, complete, run, commit, module-state wait, and reset functions.

## Control Flow
The top-level flow initializes CDB, sends a start notification, queries firmware-management features, downloads the image, runs the image, frees and reinitializes CDB because the module reset may change settings, commits the image, performs an ethtool PHY reset, and sends completion. Download starts with firmware size and vendor bytes from the beginning of the firmware payload. LPL writes chunk firmware into command payloads sized by read/write extension. EPL writes use a small LPL block address plus an extended payload up to 2048 bytes. Progress notifications are sent before each block.

## State, Persistence, And Dependencies
The operation persistently changes module firmware. It also uses `dev->ethtool->module_fw_flash_in_progress` indirectly through surrounding module-flash orchestration and notifiers. Dependencies include CMIS CDB helpers, kernel firmware blobs, netdev ops locking for reset, `ethtool_ops->reset`, and module firmware notification helpers.

## Integration Points
The module firmware flashing netlink path in `module.c` invokes `ethtool_cmis_fw_update()`. CDB command execution is delegated to `cmis_cdb.c`. Userspace receives `start`, `in_progress`, `complete`, or `err` notifications through the ethtool module firmware notification path.

## Risks
Firmware update is high impact: interrupted writes, wrong write mechanism selection, bad block addressing, or incorrect start payload size can leave modules unusable. The code treats `BOTH` as EPL, so module behavior for dual support must match that preference. Reinitializing after run-image is required; failures there must still emit final errors. Reset calls depend on driver support and lock correctness.

## Test Signals
Test with simulated modules supporting no write mechanism, LPL only, EPL only, and both. Cover firmware sizes smaller than vendor-data start size, exact block boundaries, large EPL multi-block images, command failure at each phase, module-state timeout after run, CDB reinit failure, reset failure, and notification ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/cmis_fw_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/coalesce.c -->
# sources/distributed-fs/ceph-client/net/ethtool/coalesce.c

## Purpose
This file implements the ethtool netlink get/set interface for interrupt moderation, packet coalescing, CQE mode, TX aggregation, RX CQE parameters, and dynamic interrupt moderation profiles.

## Important APIs, Types, And Functions
Public objects are `ethnl_coalesce_get_policy`, `ethnl_coalesce_set_policy`, and `ethnl_coalesce_request_ops`. Key local types are `coalesce_req_info` and `coalesce_reply_data`. Important helpers include `attr_to_mask()`, `coalesce_prepare_data()`, `coalesce_reply_size()`, `coalesce_fill_reply()`, `ethnl_set_coalesce_validate()`, `ethnl_update_irq_moder()`, `ethnl_update_profile()`, `__ethnl_set_coalesce()`, and `ethnl_set_coalesce()`.

## Control Flow
GET records driver-supported parameter bits, calls `get_coalesce()`, then emits only supported or nonzero attributes plus optional DIM RX/TX profile nests under RCU. SET first verifies `get_coalesce`/`set_coalesce` and rejects unsupported attributes based on driver-supported coalesce bits plus available DIM profile flags. It reads current driver settings, applies supplied numeric and boolean attributes, updates DIM profiles by duplicating old profile arrays and RCU-swapping new ones, then calls `set_coalesce()`. If a request changes both operation mode and parameters, it calls the driver twice so mode resets do not discard user parameter changes.

## State, Persistence, And Dependencies
Persistent effects are driver coalescing configuration and RCU-published DIM profile arrays on `dev->irq_moder`. The file depends on `linux/dim.h`, ethtool ops, shared netlink update helpers, supported-parameter bit layout, and RCU memory reclamation through `kfree_rcu()`.

## Integration Points
The request ops are registered for coalesce GET/SET/notification messages. Legacy ioctl coalescing shares the same driver callbacks, while this file exposes richer netlink attributes and DIM profile controls.

## Risks
The build-time static assertions rely on ethtool coalesce bit constants matching netlink attribute offsets. Unsupported-parameter filtering must include DIM profile bits only when the netdevice actually has those profiles. Profile parsing currently iterates supplied profile nests into fixed `NET_DIM_PARAMS_NUM_PROFILES` storage; malformed overlong nest counts are a boundary to watch. Dual mode/parameter changes are driver-sensitive.

## Test Signals
Tests should cover unsupported attributes, zero-valued unsupported fields omitted from GET, CQE mode toggles, TX aggregation values, RX/TX DIM profile reads and writes, unsupported DIM subfields, dual mode/parameter SET, no-op SET, and RCU-safe profile replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/coalesce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/common.c -->
# sources/distributed-fs/ceph-client/net/ethtool/common.c

## Purpose
This shared ethtool implementation file provides string tables, link-mode metadata, legacy conversion helpers, channel/RSS validation, timestamp/PHC discovery, PHY ops registration, RSS context lifecycle helpers, RSS indirection resize helpers, and link-medium parsing used by both ioctl and netlink ethtool paths.

## Important APIs, Types, And Functions
It exports name tables for netdev features, RSS hash functions, tunables, PHY tunables, link modes, debug classes, Wake-on-LAN modes, timestamping names, timestamp flags, and UDP tunnel types. Important functions include `convert_legacy_settings_to_link_ksettings()`, `__ethtool_get_link()`, `ethtool_get_rx_ring_count()`, `ethtool_check_max_channel()`, `ethtool_rxfh_ctx_alloc()`, `ethtool_check_rss_ctx_busy()`, `ethtool_rxfh_config_is_sym()`, `ethtool_check_ops()`, `ethtool_ringparam_get_cfg()`, timestamp/PHC helpers, `ethtool_set_ethtool_phy_ops()`, `ethtool_params_from_link_mode()`, `ethtool_forced_speed_maps_init()`, `ethtool_rxfh_context_lost()`, `netif_is_rxfh_configured()`, `ethtool_rxfh_indir_lost()`, RSS resize helpers, and `ethtool_str_to_medium()`.

## Control Flow
Static tables are initialized at build time with `static_assert()` coverage against enum sizes. Channel validation queries ntuple rules, RSS contexts, default RSS indirection, and memory-provider queue requirements before allowing channel reductions. Timestamp discovery prefers an explicit hwtstamp provider when present, otherwise checks default PHY timestamping and then netdev callbacks, always adding software timestamping capabilities. RSS context loss erases xarray entries and notifies userspace. RSS resize validation checks user-configured patterns can be shrunk or expanded without data loss, then resize helpers replicate existing patterns and notify contexts.

## State, Persistence, And Dependencies
The file mutates in-memory netdevice ethtool state: RSS context xarrays, default RSS user-size markers, registered global PHY ops pointer, and caller-provided config structs. It depends on netdevice internals, PHY topology, PTP clocks, hwtstamp providers, xarray, mutex/RCU locking, netdev queue/memory provider helpers, and ethtool netlink notifications.

## Integration Points
Feature-specific ethtool files depend on the exported string tables and validation helpers. Drivers rely on exported RSS and link-mode utilities. The legacy ioctl path and netlink path both use these shared helpers to keep behavior aligned.

## Risks
String table and link-mode metadata must stay in enum order or userspace names and bitsets break. Channel validation must not miss active RSS/ntuple/memory-provider references when reducing queues. RSS resize logic assumes periodic tables for safe shrinking. Timestamp provider selection must avoid reporting the wrong PHC source. Locking requirements around RTNL and `rss_lock` are enforced with warnings but still depend on callers.

## Test Signals
Signals include static assertion build failures after enum changes, channel reductions blocked by RSS/ntuple/memory provider state, timestamp info tests for netdev vs PHY vs explicit providers, RSS context loss notifications, RSS resize can/cannot cases for periodic and non-periodic tables, and link-medium string parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/common.h -->
# sources/distributed-fs/ceph-client/net/ethtool/common.h

## Purpose
This header exposes shared ethtool constants, string tables, global operation pointers, and helper prototypes to ethtool ioctl and netlink implementation files.

## Important APIs, Types, And Functions
Important definitions include `ETHTOOL_DEV_FEATURE_WORDS`, `ETHTOOL_LINK_MODE()`, timestamp bit-count macros, and declarations for all shared ethtool string tables. It declares helpers for link status, legacy conversion, channel validation, RSS context allocation/busy checks, RSS hash symmetry checks, ring parameter config, RX ring count, timestamp/PHC lookup, hwtstamp qualifier support, module EEPROM calls, MAC Merge support, and RSS notifications. It also declares global pointers `ethtool_phy_ops` and `ethtool_pse_ops`.

## Control Flow
The header has no runtime control flow. It defines compile-time glue used by consumers to reach implementations in `common.c`, ioctl code, netlink code, PHY/PSE code, and module EEPROM code. The `ethtool_rss_notify()` wrapper becomes a no-op when ethtool netlink is disabled.

## State, Persistence, And Dependencies
The header owns no state, but exposes global ops pointers and functions that mutate netdevice ethtool state. It depends on Linux netdevice and ethtool public headers plus forward declarations for generic netlink and hwtstamp provider descriptors.

## Integration Points
Nearly every file in `net/ethtool` includes this header for common names and validation APIs. It keeps shared helpers out of individual feature files and provides conditional compatibility when netlink support is absent.

## Risks
Changing prototypes or macro semantics can break many ethtool feature handlers. Conditional `ethtool_rss_notify()` behavior must match build configuration so code can call it unconditionally without unresolved symbols. Global ops pointer declarations require careful initialization under the right locks.

## Test Signals
Build tests with and without `CONFIG_ETHTOOL_NETLINK`, plus compile coverage of ioctl, netlink, PHY, PSE, and module EEPROM paths, are the main signals. Runtime signals come from common helper users such as channel SET, RSS notifications, timestamp queries, and module EEPROM access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/debug.c -->
# sources/distributed-fs/ceph-client/net/ethtool/debug.c

## Purpose
This file implements ethtool netlink GET/SET support for a device driver's debug message mask. It exposes `get_msglevel`/`set_msglevel` through a named bitset of netif message classes.

## Important APIs, Types, And Functions
Important local types are `debug_req_info` and `debug_reply_data`. Public objects are `ethnl_debug_get_policy`, `ethnl_debug_set_policy`, and `ethnl_debug_request_ops`. Core functions are `debug_prepare_data()`, `debug_reply_size()`, `debug_fill_reply()`, `ethnl_set_debug_validate()`, and `ethnl_set_debug()`.

## Control Flow
GET checks for `get_msglevel`, reads the mask inside ethtool ops bracketing, sizes and emits it with `ethnl_bitset32_size()`/`ethnl_put_bitset32()`, using compact format when requested. SET validates that both get and set callbacks exist, reads the current mask, applies the nested bitset update by named debug class, exits if unchanged, and calls `set_msglevel()`.

## State, Persistence, And Dependencies
The persistent state is driver-owned message-level configuration. The file depends on `bitset.c` helpers, `netif_msg_class_names`, ethtool ops callbacks, and generic netlink request infrastructure.

## Integration Points
Registered request ops cover `ETHTOOL_MSG_DEBUG_GET`, SET, and notifications. The debug class names come from `common.c`, giving userspace a stable mapping between bit positions and debug categories.

## Risks
Drivers can implement get without set or vice versa; SET correctly rejects incomplete support. Bitset parsing must reject unknown names or indices beyond `NETIF_MSG_CLASS_COUNT`. Userspace may use compact or verbose formats, so both must stay compatible.

## Test Signals
Tests should cover unsupported callbacks, compact and verbose mask reads, named class updates, no-op updates, invalid names/indices, and successful driver callback invocation with the expected mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/eee.c -->
# sources/distributed-fs/ceph-client/net/ethtool/eee.c

## Purpose
This file implements ethtool netlink GET/SET support for Energy Efficient Ethernet settings. It exposes supported, advertised, and link-partner EEE link modes plus enablement and TX LPI controls.

## Important APIs, Types, And Functions
Important local types are `eee_req_info` and `eee_reply_data`. Public objects are `ethnl_eee_get_policy`, `ethnl_eee_set_policy`, and `ethnl_eee_request_ops`. Core functions are `eee_prepare_data()`, `eee_reply_size()`, `eee_fill_reply()`, `ethnl_set_eee_validate()`, and `ethnl_set_eee()`.

## Control Flow
GET requires `get_eee`, calls it inside ops bracketing, sizes and emits advertised/supported modes as a value/mask bitset, emits peer advertised modes as a list bitset, then emits active/enabled/TX-LPI fields. SET requires both get and set callbacks, reads current EEE state, applies a link-mode bitset update to `advertised`, updates boolean and timer fields, exits if unchanged, and calls `set_eee()`.

## State, Persistence, And Dependencies
State is held by the driver and represented as `struct ethtool_keee`. The file mutates only a local copy before calling `set_eee()`. Dependencies include shared link mode names, bitset helpers, ethtool ops, and generic netlink request infrastructure.

## Integration Points
The request ops register EEE GET/SET/notification behavior in the ethtool netlink dispatcher. Link mode bit naming is shared with link modes and FEC handling through `common.c`.

## Risks
EEE settings combine advertised capabilities and policy booleans; allowing unsupported advertised bits depends on driver validation in `set_eee()`. Timer units and boolean u8 conversion must match userspace ABI. Compact and verbose bitset behavior must remain consistent for large link-mode bitmaps.

## Test Signals
Test unsupported callbacks, GET reply sizing for compact/verbose mode, advertised mode updates by name and index, enable/TX-LPI toggles, TX LPI timer updates, no-op SET, and driver rejection of invalid advertised combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/eee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/eeprom.c -->
# sources/distributed-fs/ceph-client/net/ethtool/eeprom.c

## Purpose
This file implements ethtool netlink module EEPROM reads, including page/bank-aware module access and a fallback to the older `get_module_info` plus `get_module_eeprom` API.

## Important APIs, Types, And Functions
Important local types are `eeprom_req_info` and `eeprom_reply_data`. Public objects are `ethnl_module_eeprom_request_ops` and `ethnl_module_eeprom_get_policy`. Core helpers include `fallback_set_params()`, `eeprom_fallback()`, `get_module_eeprom_by_page()`, `eeprom_prepare_data()`, `eeprom_parse_request()`, `eeprom_reply_size()`, `eeprom_fill_reply()`, and `eeprom_cleanup_data()`.

## Control Flow
Parsing requires offset, length, page, and I2C address, then enforces half-page and page-boundary constraints; page > 0 may not read the lower half. Preparation allocates a buffer, blocks reads during module firmware flashing, prefers SFP bus page reads, then driver page reads, and falls back to legacy module EEPROM calls on `-EOPNOTSUPP`. Replies contain the data bytes and cleanup frees the allocated buffer.

## State, Persistence, And Dependencies
The operation is read-only against module EEPROM and stores data in a per-reply heap buffer. It depends on `dev->ethtool->module_fw_flash_in_progress`, SFP bus helpers, driver `get_module_eeprom_by_page`, legacy ethtool module EEPROM calls, and netlink extack error reporting.

## Integration Points
The request ops handle `ETHTOOL_MSG_MODULE_EEPROM_GET`. CMIS CDB helpers use the same page-based module EEPROM infrastructure for firmware update operations, while this file provides the userspace read API.

## Risks
Boundary checks are important because module EEPROM pages have low/high halves and page-specific accessibility. Fallback offset translation for SFF-8472 I2C address `0x51` must match legacy ABI. Reads are blocked during firmware flashing to avoid racing management transactions. Reply sizing uses requested length while actual returned length can be shorter, so fill must use `reply->length`.

## Test Signals
Tests should cover required attribute enforcement, offset/length boundary errors, page > 0 lower-half rejection, banked reads, SFP bus path, driver page path, fallback path, firmware-flash `-EBUSY`, short reads, allocation failure, and cleanup on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/features.c -->
# sources/distributed-fs/ceph-client/net/ethtool/features.c

## Purpose
This file implements ethtool netlink GET and custom SET behavior for netdevice feature bits. It reports hardware-supported, wanted, active, and never-change features and lets userspace request changes to ethtool-controllable wanted features.

## Important APIs, Types, And Functions
Important local types are `features_req_info` and `features_reply_data`. Public objects/functions are `ethnl_features_get_policy`, `ethnl_features_request_ops`, `ethnl_features_set_policy`, and `ethnl_set_features()`. Internal helpers convert between `netdev_features_t`, `u32` arrays, and `unsigned long` bitmaps, and `features_send_reply()` sends detailed SET feedback.

## Control Flow
GET snapshots `dev->hw_features`, `wanted_features`, `features`, `NETIF_F_NEVER_CHANGE`, and an all-features mask, then emits them as named bitsets. SET requires a wanted bitset, resolves the device, locks RTNL and netdev ops, snapshots active/wanted bits, parses requested value/mask, rejects attempts to change non-ethtool feature bits, merges unchanged wanted bits from the old state, updates `dev->wanted_features` constrained by `hw_features`, calls `__netdev_update_features()`, optionally replies with wanted-vs-active and active-diff bitsets, and calls `netdev_features_change()` when active features changed.

## State, Persistence, And Dependencies
Persistent state is `dev->wanted_features` and resulting `dev->features`. Dependencies include shared bitset helpers, `netdev_features_strings`, netdevice feature update internals, RTNL and netdev ops locking, and generic netlink reply helpers.

## Integration Points
The GET request uses generic `ethnl_request_ops`, while SET has a bespoke handler because it must return detailed change feedback. Legacy ioctl feature handling shares the same netdevice feature model.

## Risks
Feature bit conversions must not drop high bits when `NETDEV_FEATURE_COUNT` approaches the width of `netdev_features_t`. SET must reject non-ethtool bits or userspace could alter immutable/internal flags. The reply distinguishes requested wanted differences from actual active changes; errors there can mislead userspace about driver acceptance.

## Test Signals
Tests should cover GET compact/verbose bitsets, SET with missing wanted attr, unknown feature bits, non-ethtool bit rejection, no-op updates, wanted bits unsupported by hardware, active feature changes, omit-reply flag, and notification on active changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/fec.c -->
# sources/distributed-fs/ceph-client/net/ethtool/fec.c

## Purpose
This file implements ethtool netlink GET/SET support for Forward Error Correction modes and optional FEC statistics. It maps legacy `ethtool_fecparam` bit flags to link-mode bitsets and exposes active FEC plus corrected/uncorrectable counters and histograms.

## Important APIs, Types, And Functions
Important local types are `fec_req_info`, `fec_reply_data`, and `fec_stat_grp`. Public objects are `ethnl_fec_get_policy`, `ethnl_fec_set_policy`, and `ethnl_fec_request_ops`. Core helpers include `ethtool_fec_to_link_modes()`, `ethtool_link_modes_to_fecparam()`, `fec_stats_recalc()`, `fec_prepare_data()`, `fec_reply_size()`, `fec_put_hist()`, `fec_put_stats()`, `fec_fill_reply()`, `ethnl_set_fec_validate()`, and `ethnl_set_fec()`.

## Control Flow
GET requires `get_fecparam`, reads current FEC settings, optionally reads stats when `ETHTOOL_FLAG_STATS` and `get_fec_stats` are available, recalculates total/per-lane groups, maps configured and active FEC bits to link modes, and emits modes, auto flag, active mode, and optional stats. SET reads current FEC, maps to link modes and auto flag, applies requested bitset and auto updates, converts back to `ethtool_fecparam`, rejects invalid extra link modes and empty FEC selections, then calls `set_fecparam()`.

## State, Persistence, And Dependencies
Persistent state is driver-owned FEC configuration changed by `set_fecparam()`. Statistics are read-only snapshots. Dependencies include shared link mode names, bitset helpers, ethtool stats initialization, `ethtool_ops` FEC callbacks, and netlink 64-bit stat attribute helpers.

## Integration Points
The request ops cover FEC GET/SET/notification messages. Link-mode naming is shared with EEE and link mode reporting. Legacy ioctl FEC paths use the same driver callbacks but a different userspace ABI.

## Risks
Only FEC NONE, RS, BASER, LLRS, and AUTO map to `ethtool_fecparam`; any leftover link-mode bits must be rejected. `ETHTOOL_FEC_OFF` is represented as link-mode FEC_NONE but active FEC omits NONE/AUTO. Histogram and per-lane stat encoding must handle `ETHTOOL_STAT_NOT_SET` consistently. Drivers returning reserved bits trigger warnings.

## Test Signals
Tests should cover each FEC mode mapping, auto flag changes, invalid extra link modes, empty mode rejection, active FEC reporting, stats with totals only and per-lane values, histogram bins, compact/verbose bitsets, and unsupported callback errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/fec.c -->

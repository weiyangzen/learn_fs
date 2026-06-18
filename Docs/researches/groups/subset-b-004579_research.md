# Research: subset-b-004579

Grouped research for Microchip VCAP API implementation, public/private headers, debugfs support, and KUnit coverage.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api.c

## Purpose
`vcap_api.c` is the central implementation of the Microchip VCAP rule API. It turns client supplied key/action fields into VCAP hardware cache bitstreams, validates keyset/actionset compatibility against generated model tables, manages rule allocation and sorted placement in VCAP address space, moves hardware rows when rule ordering changes, handles counters, and manages chained lookup enablement per port. It exports the client-facing API declared in `vcap_api_client.h` while using private state from `vcap_api_private.h`.

## Important APIs, Types, and Functions
The file uses `struct vcap_rule_internal` as the real rule object behind `struct vcap_rule`, `struct vcap_admin` as the per-instance state holder, and `struct vcap_control` for model tables plus platform callbacks. Key exported APIs include `vcap_alloc_rule`, `vcap_val_rule`, `vcap_add_rule`, `vcap_mod_rule`, `vcap_del_rule`, `vcap_get_rule`, `vcap_copy_rule`, `vcap_enable_lookups`, `vcap_find_admin`, `vcap_chain_id_to_lookup`, `vcap_rule_add_key_*`, `vcap_rule_add_action_*`, `vcap_rule_get_counter`, `vcap_rule_set_counter`, and name/lookup helpers.

Encoding is built around `vcap_stream_iter`, `vcap_iter_init`, `vcap_iter_next`, `vcap_encode_field`, `vcap_decode_field`, and `vcap_encode_typegroups`. These functions map model field offsets into packed register streams while skipping or injecting typegroup bits. Model lookup helpers such as `vcap_keyfieldset`, `vcap_keyfields`, `vcap_actionfieldset`, `vcap_actionfields`, and their typegroup/count variants validate generated model table bounds before returning metadata.

## Control Flow
Typical rule creation flows through `vcap_alloc_rule`, client field addition, `vcap_val_rule`, and `vcap_add_rule`. Validation checks the callback table with `vcap_api_check`, finds or honors a keyset, asks the platform `validate_keyset` callback to confirm port lookup support, selects an actionset if needed, adds type fields and platform default fields, computes rule size, then checks address-space capacity. `vcap_add_rule` locks the admin, decides whether the rule is permanent/enabled/disabled, inserts a duplicate into the sorted admin list, invokes hardware row movement if needed, resets the counter, and either initializes disabled hardware rows or encodes and writes entry/action streams.

Retrieval and debug decode follow the reverse path: `vcap_get_rule` locates a locked stored rule, `vcap_decode_rule` duplicates it, reads hardware cache for enabled/permanent rules, derives keyset/actionset from typegroups/type fields, and reconstructs client field lists. Disabled rules are stored with full copied key/action lists and can be returned without hardware reads.

Deletion uses `vcap_fill_rule_gap` for middle/front removals, updates addresses of following rules, calls the platform `move` callback, erases freed rows with `init`, and updates `last_used_addr`. Modification re-encodes an existing rule in place and resets counters.

## State and Persistence Behavior
Persistent driver state is in memory and hardware. `admin->rules` stores duplicated rule records ordered by `sort_key`; `admin->enabled` stores per-port chain enable records; `admin->cache` is a transient encode/decode staging area backed by platform callbacks. `last_used_addr` tracks the lowest occupied address while valid ranges are bounded by `first_valid_addr` and `last_valid_addr`. Disabled external rules persist in software with complete field lists; enabled/permanent rules persist primarily in hardware and store minimal metadata after successful enablement.

Rule IDs are unique across all admins in a `vcap_control`; id zero triggers linear auto-allocation. Counters live in hardware cache/counter selection and can be read, written, and accumulated by cookie. `vcap_get_rule_count_by_cookie` reads all matching counters, accumulates values, and resets them.

## Dependencies and Integration Points
This implementation depends on generated `vcap_ag_api.h` model enums/tables, Linux lists/mutexes/netdevice types, and platform callbacks in `struct vcap_operations`. Hardware integration is deliberately callback-based: `cache_erase`, `cache_write`, `cache_read`, `init`, `update`, `move`, `validate_keyset`, `add_default_fields`, and `port_info` are supplied by the owning Ethernet driver. TC integration is visible through `vcap_set_tc_exterr`, which maps `vcap_rule_error` to extack messages.

Debugfs consumes internal decode helpers, while KUnit includes this file under `CONFIG_VCAP_KUNIT_TEST` to test static helpers.

## Risks and Edge Cases
Bitstream correctness is sensitive to typegroup offsets, mask inversion conventions in platform callbacks, and `w32be` field byte ordering. Several helpers assume field enum values index directly into generated arrays, so callers must only use enums valid for the selected model. The sorted rule insertion and deletion move logic is address-alignment sensitive, especially for mixed rule sizes. `vcap_admin_rule_count` locks inside the list iteration rather than around the whole traversal, which is unusual and should be reviewed if concurrency behavior changes. Error paths in decode may return allocated but not freed intermediate duplicates if callers do not follow `ERR_PTR` expectations.

## Test Signals
`vcap_api_kunit.c` covers iterator math, typegroup encoding, key/action bitstream encoding, rule validation, add/delete/move placement, counter read/write, chained lookup support, and key filtering. `vcap_api_debugfs_kunit.c` exercises raw keyset discovery and debug dump formatting through decode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api.h

## Purpose
`vcap_api.h` defines the core model, rule, admin, cache, command, and callback contracts shared by VCAP API clients and the implementation. It is the foundational header that maps generated VCAP model metadata to runtime rule administration.

## Important APIs, Types, and Constants
The chain constants (`VCAP_CID_*`, `VCAP_CID_LOOKUP_SIZE`) define reserved chain-id ranges for ingress, prerouting, stage 2, and egress lookups. `enum vcap_user` orders known rule owners and is used in rule sort keys. `struct vcap_field`, `struct vcap_set`, `struct vcap_typegroup`, and `struct vcap_info` describe generated key/action field layouts, keysets/actionsets, typegroup bits, and per-VCAP dimensions. `struct vcap_cache_data` defines the hardware cache staging streams.

`struct vcap_admin` is the per-instance runtime state: admin list linkage, rule and enabled-port lists, mutex, VCAP type/instance identifiers, chain range, target instance, lookup counts, valid address range, `last_used_addr`, word-ordering flag, traffic direction, and cache. `struct vcap_rule` is the client-visible rule with chain id, user, priority, id, cookie, key/action lists, selected keyset/actionset, extended error, and client scratch value.

`struct vcap_operations` is the hardware/platform callback table. `struct vcap_control` binds callbacks, model metadata, stats/name tables, and the admin list.

## Control Flow and Integration
The header does not implement behavior, but it defines the state consumed by `vcap_api.c`, debugfs, and platform drivers such as Microchip switch drivers. Clients allocate rules, fill `keyfields` and `actionfields`, and call client APIs; the implementation validates against `vcaps`, stages data in `vcap_cache_data`, and delegates actual hardware access to `vcap_operations`.

## State and Persistence Behavior
The runtime state declared here is long-lived driver memory. Rule lists and enabled-port lists are protected by `vcap_admin.lock`; hardware persistence is abstracted through cache/update/init/move callbacks. `last_used_addr` and valid address bounds are critical for persistent hardware layout across rule additions and deletions.

## Dependencies
The header depends on Linux `types`, `list`, `netdevice`, and the generated model header `vcap_ag_api.h`. It intentionally avoids including debugfs or KUnit specifics.

## Risks and Test Signals
The main risk is contract drift between generated model arrays and enum/index usage. Misconfigured `sw_width`, `act_width`, typegroup maps, or callback tables will break encoding at runtime. KUnit tests use this header extensively through mocked `struct vcap_control`, `struct vcap_admin`, and cache streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_client.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_client.h

## Purpose
`vcap_api_client.h` is the client-facing API for constructing, validating, installing, modifying, querying, and deleting VCAP rules. It also defines typed key/action value containers used by drivers and TC offload code.

## Important APIs and Types
The file defines key/action control wrappers (`vcap_client_keyfield_ctrl`, `vcap_client_actionfield_ctrl`), fixed-width key/action value types from bit to 128 bits, and union containers for field data. Keys carry value plus mask; actions carry value only. `enum vcap_bit` provides `ANY`, `0`, and `1` semantics, and `struct vcap_counter` carries packet count and sticky hit state.

The API surface includes lookup enabling (`vcap_enable_lookups`), rule lifecycle (`vcap_alloc_rule`, `vcap_free_rule`, `vcap_val_rule`, `vcap_add_rule`, `vcap_del_rule`, `vcap_get_rule`, `vcap_mod_rule`, `vcap_copy_rule`), explicit keyset/actionset selection, key/action field addition and modification, counter operations, chain/lookup helpers, name helpers, TC extack conversion, key filtering, and action lookup.

## Control Flow
Clients normally allocate a rule, add key and action fields using the typed helpers, optionally force keyset/actionset or counter id, validate the rule, add it, then free their owned copy. Later they can fetch a decoded copy with `vcap_get_rule`, modify fields with `vcap_rule_mod_key_u32` or `vcap_rule_mod_action_u32`, and call `vcap_mod_rule`. Deletion and counter operations are keyed by `vcap_control`, netdev, id, cookie, or rule pointer depending on the operation.

## State and Persistence Behavior
The header makes ownership boundaries explicit: `vcap_alloc_rule` returns client-owned memory, `vcap_add_rule` stores an internal duplicate, and `vcap_free_rule` frees the client copy. Rule ids are unique within the control; cookie is client-supplied and can aggregate counters. Enabled lookup state is managed by cookie and netdev.

## Dependencies and Integration Points
The header depends on Linux netdevice/list/types, `net/flow_offload.h` for TC extack, and `vcap_api.h` for core model/admin/rule definitions. It is the expected include for platform and offload clients that do not need private internals.

## Risks and Test Signals
Callers must avoid duplicate fields and must keep field type width aligned with generated model metadata. Some helpers only expose selected widths (`u48`, `u72`, `u128` for keys and `u72` for actions), so unsupported widths require API extension. KUnit verifies value insertion, keyset/actionset discovery, field filtering, counters, and lookup-chain helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs.c

## Purpose
`vcap_api_debugfs.c` implements read-only debugfs views for VCAP state. It exposes per-port callback output, full decoded VCAP instance dumps, and raw address/keyset scans for diagnosing installed rules and hardware layout.

## Important APIs and Functions
The exported entry points are `vcap_port_debugfs` and `vcap_debugfs`. Internally, `vcap_debugfs_show_rule_keyfield` and `vcap_debugfs_show_rule_actionfield` format typed values, including IPv4, IPv6, MAC, decimal, and hex representations. `vcap_debugfs_show_keysets`, `vcap_debugfs_show_rule_keyset`, `vcap_debugfs_show_rule_actionset`, and `vcap_show_admin_rule` compose a decoded rule dump. `vcap_show_admin_info` prints model/admin metadata. `vcap_show_admin` decodes each stored rule, while `vcap_show_admin_raw` scans addresses and calls `vcap_addr_keysets`.

## Control Flow
`vcap_debugfs` creates a `vcaps` directory, then for each admin creates `raw_<name>_<instance>` and `<name>_<instance>` files. The normal view locks the admin, decodes each rule through `vcap_decode_rule`, prints metadata and fields, then frees the decoded copy. The raw view locks the admin, walks from `last_valid_addr` down to `first_valid_addr`, identifies keysets at each address, and prints aligned rule starts. `vcap_port_debugfs` creates a netdev-named file whose show callback delegates to the platform `port_info` callback for each instance zero admin.

## State and Persistence Behavior
Debugfs files store small `devm_kzalloc` info wrappers pointing at existing `vcap_control`, `vcap_admin`, and `net_device` objects. They do not own rules or hardware state. Show paths read hardware through the same cache/decode functions as the API and are serialized by `admin->lock`.

## Dependencies and Integration Points
The file depends on `debugfs`, `seq_file` show attributes, private VCAP internals, name/stat tables, and platform callbacks. It integrates with the public `vcap_api_debugfs.h` stubs so callers can compile without debugfs.

## Risks and Test Signals
Debugfs reads can be expensive because full dumps decode rules and raw dumps scan address ranges. Formatting assumes generated name tables cover all enum values being printed. The U32 formatter uses bit masks based on field width and must avoid invalid full-width shifts; the code handles width 32 specially for keyfields, but actionfield U32 formatting should be considered carefully if width can be 32. KUnit covers admin metadata output, full decoded rule output, and raw keyset scanning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs.h

## Purpose
`vcap_api_debugfs.h` declares the optional debugfs integration for the VCAP API and provides no-op stubs when `CONFIG_DEBUG_FS` is disabled.

## Important APIs
When debugfs is enabled, `vcap_port_debugfs` creates a per-port debugfs file for platform port information and `vcap_debugfs` creates per-VCAP instance debugfs entries. When disabled, `vcap_port_debugfs` compiles to an empty inline and `vcap_debugfs` returns `NULL`.

## Control Flow and State
The header only selects compile-time behavior. It keeps callers simple: platform drivers can call these helpers unconditionally and receive either real debugfs entries or no-op behavior. No state is owned in the header.

## Dependencies and Integration
The enabled declarations depend on Linux `debugfs`, `device`, `net_device`, and `vcap_control`. The implementation lives in `vcap_api_debugfs.c`; callers include this header to avoid directly depending on private internals.

## Risks and Test Signals
The main risk is assuming a non-NULL `struct dentry *` from `vcap_debugfs` when debugfs is disabled or creation fails. Debugfs behavior is covered indirectly by `vcap_api_debugfs_kunit.c` when compiled into the implementation under the VCAP KUnit config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs_kunit.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs_kunit.c

## Purpose
`vcap_api_debugfs_kunit.c` tests the debugfs and raw decode helpers by embedding a mocked VCAP platform, generated KUnit model tables, and expected text output. It is included from `vcap_api_debugfs.c` under `CONFIG_VCAP_KUNIT_TEST`, allowing tests to reach static helpers.

## Important Fixtures and Tests
The fixture defines mock cache streams, a mock netdev, platform callbacks for keyset validation, default fields, cache read/write/update/move/init, and a print collector (`test_prf`). `vcap_api_addr_keyset_test` scans synthetic IS2 key/mask streams and expects only the real rule start to decode as `VCAP_KFS_MAC_ETYPE`. `vcap_api_show_admin_raw_test` verifies raw address output. `vcap_api_show_admin_test` validates admin metadata formatting. `vcap_api_show_admin_rule_test` verifies full decoded rule output including keysets, key/action fields, counter, state, and field formatting.

## Control Flow
Each test initializes a `vcap_admin`, attaches it to `test_vctrl`, configures cache stream pointers, invokes internal debugfs helpers, and compares collected output lines. Cache read inverts mask words to emulate hardware mask conventions before decode.

## State and Persistence Behavior
State is test-local static fixture state reset by `vcap_test_api_init`. No persistent repository state is produced. The tests exercise both in-memory rule metadata and cache-backed decode paths.

## Dependencies and Integration Points
The file depends on KUnit, `vcap_model_kunit.h`, public VCAP headers, and debugfs implementation internals exposed by textual inclusion. It mirrors the callback contract used by real platform drivers but with deterministic arrays.

## Risks and Test Signals
These tests provide strong regression signals for debug output formatting and keyset discovery. They are brittle by design: expected strings encode exact field order, names, widths, and formatting, so generated model changes require synchronized expectation updates. They do not test actual debugfs file creation failures or lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_kunit.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_kunit.c

## Purpose
`vcap_api_kunit.c` is the main KUnit suite for the VCAP API implementation. It validates low-level stream encoding, model lookup helpers, key/action value insertion, rule validation, hardware write address sequencing, rule ordering and deletion movement, counter operations, key filtering, and chained lookup path logic.

## Important Fixtures and Test Suites
The file builds a mocked platform around `test_callbacks`, `test_vctrl`, synthetic cache arrays, and `vcap_test_api_init`. `test_val_keyset` models platform keyset selection for IS0/IS2, `test_add_def_fields` injects lookup defaults, and cache callbacks record writes, reads, moves, init ranges, and counter state.

Test suites include encoding (`VCAP_API_Encoding_Testsuite`), rule values, full rule behavior, support helpers, counters, insertion, removal, and rule-enable path behavior. Helper `test_vcap_xn_rule_creator` creates rules of specific subword sizes to exercise sorting and address allocation.

## Control Flow Covered
Encoding tests directly call static helpers for bit setting, iterator initialization/advance, typegroup injection, field encoding across register/subword boundaries, max-width key fields, and action fields. Rule tests allocate rules, add duplicate and valid fields, validate model selection, enable lookups, add rules, assert hardware update address sequences, disable/delete rules, and free client copies. Insert/remove tests create mixed-size rules and assert exact addresses and hardware move parameters. Chain tests validate next-lookup detection and path traversal through enabled-port records.

## State and Persistence Behavior
The test harness emulates hardware state in static arrays and records side effects in globals such as `test_updateaddr`, `test_hw_cache`, `test_move_*`, and `test_init_*`. It validates that API calls mutate admin rule lists, `last_used_addr`, counters, and enabled-path state as intended.

## Dependencies and Integration Points
The suite depends on KUnit, generated `vcap_model_kunit.h`, public client/core headers, and static access through inclusion from `vcap_api.c`. It tests the API at both unit-helper and lifecycle levels without real hardware.

## Risks and Test Signals
The suite is a high-value safety net for bit-packing and rule movement regressions. It also documents expected address packing: larger rules sort before smaller ones, mixed insertion may move existing rows, and deletions erase/move precise ranges. Gaps remain around allocation failure paths, concurrent access, actual platform callback failures, and all generated model combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_private.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_private.h

## Purpose
`vcap_api_private.h` defines internal-only rule state and helper prototypes shared between the core VCAP implementation, debugfs, and KUnit-included code. It separates client-visible `struct vcap_rule` from the implementation’s admin, hardware address, size, state, and counter metadata.

## Important APIs and Types
`to_intrule(rule)` converts a public rule pointer to `struct vcap_rule_internal`. `enum vcap_rule_state` distinguishes permanent hardware rules, enabled external rules, and disabled software-cached rules. `struct vcap_rule_internal` embeds `struct vcap_rule` and adds list linkage, admin/netdev/control pointers, sort key, key/action subword and register sizes, total rule size, hardware address, counter id/cache, and state. `struct vcap_stream_iter` tracks bit offsets, subword widths, register index/bit position, and current typegroup while encoding or decoding streams.

The header declares internal validation/cache helpers, iterator functions, model metadata accessors, keyset/actionset name helpers, raw keyset discovery (`vcap_addr_keysets`, `vcap_find_keystream_keysets`), keyset derivation for rules, and `vcap_decode_rule`.

## Control Flow and State
Core API functions allocate `vcap_rule_internal` but return the embedded public rule. Rule insertion stores duplicates of this internal object in `admin->rules`. Debugfs uses the declared decode and model helpers to inspect rules without reimplementing bitstream logic.

## Dependencies and Integration Points
The header depends on Linux types and both public VCAP headers. It is intentionally not for normal clients; external drivers should include `vcap_api_client.h` instead.

## Risks and Test Signals
The pointer conversion macro requires the public rule to be embedded exactly as the first intended member of `vcap_rule_internal`; misuse with non-internal rule memory would corrupt state. The private API is tightly coupled to generated model indexes and hardware cache layout. KUnit exercises many declared helpers through textual inclusion of implementation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_private.h -->

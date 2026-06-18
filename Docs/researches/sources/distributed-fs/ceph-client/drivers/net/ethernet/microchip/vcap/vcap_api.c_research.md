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

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

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

# sources/distributed-fs/ceph-client/net/xfrm/xfrm_hash.h

Purpose: `xfrm_hash.h` defines inline hash functions used by XFRM state and policy lookup tables, plus declarations for the allocation helpers in `xfrm_hash.c`.

Important APIs: Address helpers hash IPv4 and IPv6 addresses, destination/source pairs, prefixes, SPI/protocol/family tuples, replay sequence numbers, policy indexes, selectors, and explicit address/prefix pairs. `__sel_hash()` returns `hmask + 1` when a selector is less specific than configured hash thresholds, signaling callers to use inexact handling rather than a normal bucket.

Control flow: IPv4 address hashes mostly use host-order arithmetic plus Jenkins hashing for prefixes. IPv6 uses `jhash2()` across 128-bit addresses or prefix-sized words with an incomplete-word mask. Final bucket selection folds high bits and masks with caller-provided `hmask`.

State and persistence: No state is stored. Hash quality directly affects runtime distribution of state/policy buckets and lookup cost.

Dependencies and integration: Included by `xfrm_policy.c`, `xfrm_state.c`, and `xfrm_hash.c`. It depends on `xfrm_address_t`, selectors, address families, and `jhash` helpers. Hash threshold behavior integrates with policy inexact matching trees.

Risks: Hash changes alter bucket placement and can regress lookup performance or resizing behavior. Prefix masking must handle zero and partial prefixes correctly. Endianness mistakes would break IPv4 bucket consistency. The sentinel `hmask + 1` must not be treated as an actual bucket by callers.

Test signals: Add policies and states for IPv4/IPv6, exact and prefix selectors, zero-length prefixes, SPI collisions, and large hash tables. Validate lookup correctness before/after hash resize and with inexact policy thresholds.

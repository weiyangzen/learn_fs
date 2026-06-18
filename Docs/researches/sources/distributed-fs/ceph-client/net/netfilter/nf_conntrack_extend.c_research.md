# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_extend.c

## Purpose
`nf_conntrack_extend.c` implements dynamic extension storage for `struct nf_conn`. It lets optional subsystems attach helper, NAT, sequence adjustment, accounting, event cache, timestamp, timeout, labels, synproxy, and act_ct data before confirmation.

## Important APIs, Types, And Functions
`nf_ct_ext_type_len[]` maps extension IDs to structure sizes based on config. `total_extension_size()` validates the u8 offset/length design. `nf_ct_ext_add()` appends a zeroed extension to `ct->ext`, reallocating with a preallocation floor. `__nf_ct_ext_find()` validates an extension ID and generation. `nf_ct_ext_bump_genid()` invalidates old extension pointers during teardown/reconfiguration and waits one second.

## Control Flow
Extension add is only safe for unconfirmed conntracks. It computes an aligned offset, grows storage, initializes offsets and generation for a new extension block, records offset/length, zeroes the added region, and returns the new extension pointer. Lookup rejects missing or generation-stale extensions unless the gen id has been zeroed after confirmation by core insertion.

## State And Persistence
State is per-conntrack heap allocation plus the global atomic extension generation. Extension storage lives until the conntrack is freed.

## Dependencies And Integration Points
Every optional conntrack subsystem that stores per-flow data depends on this allocator. Conntrack core validates extension generation around insertion and bumps genid during module cleanup to prevent stale helper pointers from being found.

## Risks
The u8 offset/length layout imposes a hard 255-byte total extension limit, guarded by build-time checks. Adding extension types requires updating both size tables. Reallocating confirmed conntracks would race readers and is warned against. Generation invalidation must stay paired with core insertion and destroy iteration rules.

## Test Signals
Test combinations of enabled config extensions, repeated add of same ID returning NULL, allocation failure, unconfirmed-only warnings, lookup before/after genid bump, insertion after stale genid returning `-EAGAIN`, and build-time failure when extension count/size exceeds limits.

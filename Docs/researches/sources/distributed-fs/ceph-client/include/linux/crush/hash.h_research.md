<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/hash.h -->
# sources/distributed-fs/ceph-client/include/linux/crush/hash.h

## Purpose

`hash.h` declares CRUSH hash identifiers and fixed-arity hash helpers used by Ceph placement calculations. The source was read as a complete 24-line file.

## Important APIs, Types, and Functions

It defines `CRUSH_HASH_RJENKINS1` and `CRUSH_HASH_DEFAULT`. APIs include `crush_hash_name()`, `crush_hash32()`, `crush_hash32_2()`, `crush_hash32_3()`, `crush_hash32_4()`, and `crush_hash32_5()`.

## Control Flow

CRUSH bucket selection calls these hash helpers with stable placement inputs such as object hash, replica index, bucket IDs, and retry counters. The hash type selects the concrete algorithm.

## State and Persistence Behavior

No state is stored. Determinism across kernel and userspace implementations is the key persistence property because object placement must remain stable across boots and clients.

## Dependencies and Integration Points

It uses Linux types in kernel builds or `crush_compat.h` outside the kernel. It integrates with `crush.h` bucket `hash` fields and the CRUSH mapper.

## Risks and Edge Cases

Changing hash behavior or constants changes data placement. Unsupported hash type handling must stay consistent with map decoding and userspace Ceph.

## Test Signals

Signals include fixed hash vectors for each arity, CRUSH mapping determinism tests, kernel/userspace hash comparison, and invalid hash type handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crush/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kernel.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/kernel.h

## Purpose
This is a compact tools replacement for common kernel utility macros, endian conversions, assertion hooks, and snprintf helpers.

## APIs And Flow
It includes libc and tools headers, defines `UINT_MAX`, `_RET_IP_`, `PERF_ALIGN`, `offsetof`, type-safe `min`, `max`, `min_t`, `max_t`, `clamp`, `BUG_ON`, `BUG`, endian conversion aliases, `vscnprintf()`, `scnprintf()`, `scnprintf_pad()`, `ARRAY_SIZE`, `current_gfp_context()`, and `synchronize_rcu()`. Flow is inline macro evaluation with single-evaluation min/max temporaries and host-endian conversion selection from `__BYTE_ORDER`.

## State, Dependencies, Risks, Tests
No persistent state is stored here. Dependencies include libc headers, `asm/bug.h`, `byteswap.h`, `assert.h`, `linux/build_bug.h`, and `linux/compiler.h`. Risks are weaker kernel semantics: `BUG_ON` becomes `assert` unless `NDEBUG`, RCU synchronization is a no-op, and endian conversion macros are function-like aliases. Tests should cover debug and `NDEBUG` builds, endian conversions on both byte orders, ARRAY_SIZE type checking, and snprintf truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kernel.h -->

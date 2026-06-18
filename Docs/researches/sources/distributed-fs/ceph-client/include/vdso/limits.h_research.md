<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/limits.h -->
# sources/distributed-fs/ceph-client/include/vdso/limits.h

Purpose: provides a small limits header for vDSO code that cannot rely on full kernel or libc limits.

Important APIs and types: defines signed and unsigned min/max constants for short, int, long, long long, unsigned variants, and `UINTPTR_MAX`.

Control flow: other vDSO headers use these constants, notably `INT_MAX` for the time namespace clock mode marker.

State and persistence: no state.

Dependencies and integration points: standalone; integrates with `vdso/clocksource.h` and other low-level headers.

Risks and test signals: risks include type-size assumptions on unusual architectures. Test vDSO builds on 32/64-bit and compat configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/limits.h -->

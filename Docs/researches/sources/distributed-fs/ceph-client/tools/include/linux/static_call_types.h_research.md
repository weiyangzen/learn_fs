<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/static_call_types.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/static_call_types.h

## Purpose
This header defines static-call symbol naming, site metadata, and dispatch structures used by kernel and tooling builds.

## APIs And Flow
It exports key and trampoline prefix macros, string forms, site flags, `struct static_call_site`, `DECLARE_STATIC_CALL()`, `struct static_call_key`, and `static_call()` or `static_call_mod()` forms selected by `CONFIG_HAVE_STATIC_CALL`, `CONFIG_HAVE_STATIC_CALL_INLINE`, and `MODULE`. With inline static calls, key symbols are marked addressable so objtool can create `.static_call_sites`; without static call support, calls dereference the key's function pointer.

## State, Dependencies, Risks, Tests
State is in static call keys, trampolines, and generated site tables. Dependencies are `linux/types.h`, `linux/stringify.h`, `linux/compiler.h`, objtool, and architecture static-call support. Risks include stripped key symbols, wrong low-bit site flags, module versus built-in dispatch differences, and stale tooling metadata. Tests should build with each config combination, inspect static-call site sections, and verify fallback function-pointer dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/static_call_types.h -->

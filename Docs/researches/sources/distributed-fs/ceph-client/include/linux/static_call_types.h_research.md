<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_call_types.h -->
# sources/distributed-fs/ceph-client/include/linux/static_call_types.h

Purpose: Defines shared static-call symbol naming, site metadata, declarations, call expression macros, and `struct static_call_key` layouts used by `static_call.h` and architecture code.

Important APIs/types/functions: `STATIC_CALL_KEY_PREFIX`, `STATIC_CALL_KEY()`, `STATIC_CALL_TRAMP_PREFIX`, `STATIC_CALL_TRAMP()`, `STATIC_CALL_SITE_*` flags, `struct static_call_site`, `DECLARE_STATIC_CALL()`, `__raw_static_call()`, `__static_call()`, `struct static_call_key`, `static_call_mod()`, and `static_call()`.

Control flow: Macro expansion constructs symbol names for keys and trampolines. With static-call support, `static_call()` resolves to the trampoline and may mark the key addressable for tooling. Without support, it casts the stored function pointer in the key.

State and persistence behavior: The key holds the active function pointer and, for inline-capable builds, either module metadata or static callsite pointers. Site metadata uses relative addresses and key references with low-bit flags.

Dependencies: Kernel types, stringify/paste helpers, compiler addressability support, module configuration, and architecture/tooling support.

Integration points: Included by `static_call.h`, architecture assembly/C code, objtool-generated `.static_call_sites`, and modules using static calls.

Risks: Symbol naming and addressability are part of tooling contracts; changing them breaks objtool/module linkage. Low-bit flag encoding requires aligned key pointers.

Test signals: Build/link tests for declared/defined static calls, objtool static-call site generation, module static-call use, and generic fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_call_types.h -->

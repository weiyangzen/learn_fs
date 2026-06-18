# sources/distributed-fs/ceph-client/arch/parisc/kernel/parisc_ksyms.c

Purpose: declares PA-RISC architecture symbols that loadable modules need but that are implemented by compiler helpers, assembly routines, or low-level kernel code rather than ordinary exported C APIs.

Important exports include `memset`, atomic exchange and compare-exchange helpers (`__xchg8`, `__xchg32`, optional `__xchg64`, `__cmpxchg_u8/u16/u32/u64`), SMP `__atomic_hash`, user-memory `lclear_user`, 32-bit `$global$`, PA-RISC millicode arithmetic helpers such as `$$divI`, `$$divU`, `$$remI`, `$$remU`, `$$mulI`, specialized divide variants, libgcc 64-bit shift/multiply/compare helpers, 64-bit divide/mod helpers, `__canonicalize_funcptr_for_compare`, 32-bit `$$dyncall`, optional `_mcount`, and `clear_page_asm`/`copy_page_asm` from `pacache.S`.

Control flow is compile-time only: preprocessor guards expose symbols according to `CONFIG_SMP`, `CONFIG_64BIT`, and `CONFIG_FUNCTION_TRACER`. There is no runtime behavior beyond module loader symbol resolution.

State and persistence are in the kernel module symbol table. The file is an integration point between PA-RISC ABI requirements, GCC/libgcc emitted helper calls, hand-written assembly, ftrace, and external modules. It depends on declarations from `linux/atomic.h`, `linux/libgcc.h`, `linux/uaccess.h`, and architecture I/O headers to match actual definitions elsewhere.

Risks are mostly ABI and link-time risks: removing an export can break out-of-tree or modular in-tree drivers, mismatching a helper prototype can corrupt call ABI, and 32-bit special symbols with `$` names are unusual enough to be easy to mishandle in tooling. Test signals are successful PA-RISC `modpost`, module insertion, ftrace-enabled builds, 32-bit and 64-bit allmodconfig-style builds, and lack of unresolved-symbol failures for modules using atomic, page, arithmetic, or function-pointer helpers.

# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-prototypes.h

Purpose: declares C-visible prototypes for symbols implemented in PowerPC assembly so modversions and C callers see consistent signatures.

Important APIs/types/functions: includes checksum, uaccess, string, and asm headers; declares low-level helpers such as `flush_icache_range`, `__flush_icache_range`, `_mcount`, ftrace and kprobes trampoline symbols, compare/copy/checksum helpers, and interrupt/exception entry helpers depending on configuration.

Control flow: no runtime logic. Preprocessor config gates declarations for ftrace, kprobes, KASAN, PPC32/PPC64, and exception models.

State and persistence: no state is stored. It constrains ABI contracts between assembly and C.

Dependencies and integration points: consumed by assembly build infrastructure and C modules that need symbol CRCs. It integrates exception entry, ftrace, kprobes, checksum/string routines, and user access assembly.

Risks: signature mismatch between declarations and assembly implementations can break module versioning or calling conventions. Config guards must track where the symbols are actually built.

Test signals: allmodconfig builds with `CONFIG_MODVERSIONS`, ftrace, kprobes, KASAN, PPC32, and PPC64 combinations; runtime smoke tests for tracing and checksum/string routines.


# sources/distributed-fs/ceph-client/include/linux/nvram.h

Purpose: defines a portable NVRAM operation table and wrapper helpers for architecture NVRAM access.

Important APIs/types/functions: `struct nvram_ops` may provide size, byte read/write, range read/write, and x86/m68k initialize/checksum operations. `arch_nvram_ops` is the generic architecture implementation. Inline wrappers `nvram_get_size()`, `nvram_read_byte()`, `nvram_write_byte()`, `nvram_read_bytes()`, `nvram_write_bytes()`, `nvram_read()`, and `nvram_write()` choose PPC machdep hooks when `CONFIG_PPC` is set, otherwise use `arch_nvram_ops`, falling back from range operations to byte loops.

Control flow: callers use generic wrappers. The wrappers check for architecture-provided optimized operations, fall back to byte access, update file offsets while reading/writing, and stop at reported NVRAM size.

State and persistence: NVRAM content is persistent platform storage. The header owns no state, but writes may update hardware and checksums through architecture callbacks.

Dependencies and integration points: depends on errno, UAPI NVRAM definitions, PPC `ppc_md` hooks, and architecture-specific `arch_nvram_ops`. It integrates legacy `/dev/nvram`, platform firmware variables, and architecture NVRAM backends.

Risks and test signals: risks include no size provider returning `-ENODEV`, byte fallback ignoring checksum semantics, offset truncation at device end, PPC/generic behavior divergence, and writes without checksum updates when only byte hooks exist. Test signals include read/write boundary tests, missing backend tests, checksum validation on x86/m68k, PPC machdep hook coverage, and persistence checks across reboot where hardware permits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvram.h -->

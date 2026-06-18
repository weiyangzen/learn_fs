<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/auxvec.h

Purpose: Defines PowerPC auxiliary vector entries exposed to ELF userspace.

Important APIs/types/functions: Cache block-size entries `AT_DCACHEBSIZE`, `AT_ICACHEBSIZE`, `AT_UCACHEBSIZE`, `AT_IGNOREPPC`, `AT_SYSINFO_EHDR`, detailed cache size/geometry entries, `AT_MINSIGSTKSZ`, and `AT_VECTOR_SIZE_ARCH`.

Control flow: ELF loader/kernel setup fills these keys in auxv; libc and applications read them for vDSO location, cache instruction safety, cache geometry, and signal stack sizing.

State and persistence: Auxv values are per-process ABI state copied at exec time.

Dependencies and integration points: Integrated with ELF binfmt, vdso setup, glibc expectations, and cache topology code.

Risks: Numeric values are ABI-stable; changing them breaks libc. Cache block versus line semantics must remain distinct.

Test signals: Inspect `/proc/self/auxv`, glibc startup/vDSO tests, cache geometry validation, and signal-stack sizing tests.

Source read size: 55 lines, 1846 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/auxvec.h -->

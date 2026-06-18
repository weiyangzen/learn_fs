<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/Makefile

Purpose: This Makefile builds the standalone s390 kexec purgatory binary, validates it for unresolved symbols, strips it to a relocatable read-only object, and embeds it into the kernel through `kexec-purgatory.o`.

Important APIs/types/functions: It defines `purgatory-y`, `PURGATORY_OBJS`, custom rules for `sha256.o` from `lib/crypto/sha256.c`, `mem.o` from `arch/s390/lib/mem.S`, targets `purgatory`, `purgatory.chk`, and `purgatory.ro`, and object inclusion `obj-y += kexec-purgatory.o`.

Control flow: Kbuild compiles freestanding purgatory objects with special CFLAGS, links `purgatory` with the linker script and `-r`, links `purgatory.chk` without `-r` to catch unresolved symbols, objcopies `purgatory.ro` while removing debug/comment/note sections, then assembles `kexec-purgatory.o` that incbins the stripped artifact.

State and persistence: The output artifact `purgatory.ro` becomes embedded kernel rodata. The Makefile intentionally avoids normal kernel runtime instrumentation, exports, stack protector, builtins, PIE, and branch profiling so the purgatory can run between kernels.

Dependencies and integration points: It depends on Kbuild, the s390 linker, objcopy, crypto SHA-256 source, s390 mem assembly, `purgatory.lds.S`, and `kexec-purgatory.S`. It integrates with the s390 kexec image loader.

Risks and test signals: Freestanding flags must stay strict because purgatory cannot rely on kernel runtime services. `purgatory.chk` is the unresolved-symbol gate. Tests include `make arch/s390/purgatory/`, kexec/kdump boot paths, objdump/readelf inspection for unwanted sections or relocations, and compiler variation with GCC/Clang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/Makefile -->

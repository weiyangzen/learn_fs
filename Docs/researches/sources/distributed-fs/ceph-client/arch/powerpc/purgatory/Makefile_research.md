<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/purgatory/Makefile

Purpose: builds the PowerPC kexec purgatory object that is embedded into the kernel and used as the transition trampoline for kexec/kdump.

Important APIs/types/functions: targets `trampoline_$(BITS).o`, `purgatory.ro`, and `kexec-purgatory.o`; `LDFLAGS_purgatory.ro` sets entry point `purgatory_start`, relocatable link, and `--no-undefined`; `KBUILD_CFLAGS` filters out PGO flags.

Control flow: the trampoline object is linked into `purgatory.ro`; `kexec-purgatory.o` depends on that binary and embeds it through `kexec-purgatory.S`; `obj-y` includes the final wrapper object in the kernel build.

State and persistence: no runtime state. The artifact is a read-only relocatable blob consumed by kexec setup code.

Dependencies and integration points: integrates with Kbuild target tracking and the PowerPC purgatory assembly sources. The PGO filter avoids LLVM producing overlapping text sections that kexec cannot handle.

Risks: entry point or link flag changes can make the purgatory blob unusable by kexec. Toolchain flags that alter section layout are sensitive because the blob is copied and patched by kexec code.

Test signals: successful `kexec_file_load`/kexec boot on ppc64, objdump/readelf showing `purgatory_start` entry and no undefineds, and builds with PGO enabled confirm this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/Makefile -->

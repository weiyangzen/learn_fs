# sources/distributed-fs/ceph-client/arch/sh/kernel/vsyscall/Makefile

Purpose: builds the SH vDSO/vsyscall objects and generates symbol metadata for the in-kernel embedded vsyscall image.

Important targets and variables: `obj-y`, `extra-y`, `targets`, `$(obj)/vsyscall-syms.o`, `$(obj)/vsyscall.so`, custom `ld` rule using `vsyscall.lds`, `nm` to generate `vsyscall-syms.S`, and stripped `objcopy` output.

Control flow: assembly sources are linked into `vsyscall.so`, symbol addresses are transformed into an assembly file, and both the syscall wrapper object and generated symbol object are included in the kernel build.

State and persistence: produces build artifacts, not runtime state. The generated symbol file must reflect the linked shared-object layout consumed by `vsyscall.c`.

Dependencies and integration: depends on the architecture linker, `nm`, `objcopy`, `vsyscall.lds.S`, and the kernel Kbuild object graph.

Risks: stale or mismatched generated symbols would corrupt vDSO symbol exposure. Toolchain differences in `nm`/`objcopy` output can affect reproducibility.

Test signals: successful Kbuild of `arch/sh/kernel/vsyscall`, generated `vsyscall-syms.S`, valid `vsyscall.so`, and process startup with a working `[vdso]` mapping.

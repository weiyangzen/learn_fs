<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/machine_kexec_reloc.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/machine_kexec_reloc.c

Purpose: Reuses the s390 kernel kexec relocation implementation inside the boot build by textual inclusion.

Important APIs/types/functions: Declares no local functions or types. The exported behavior is provided by `../kernel/machine_kexec_reloc.c`.

Control flow: The compiler processes the shared kernel relocation source as part of the boot object, allowing early code to use the same relocation routines where required.

State and persistence: No local state exists. Any state belongs to the included kexec relocation implementation.

Dependencies and integration points: Depends on the shared kernel file remaining suitable for inclusion under boot build constraints and on relative path stability. It integrates with s390 kexec/crash boot support.

Risks: The wrapper can break if the shared file gains dependencies on normal kernel runtime services, instrumentation, or section annotations incompatible with the decompressor.

Test signals: s390 kexec and crash-kernel builds, decompressor link validation, and kexec relocation tests after modifying the included kernel file.

Source read size: 2 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/machine_kexec_reloc.c -->

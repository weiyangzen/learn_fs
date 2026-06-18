<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/kexec-purgatory.S -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/kexec-purgatory.S

Purpose: This assembly file embeds the built s390 purgatory image into kernel rodata and exposes start/end/size symbols for kexec code.

Important APIs/types/functions: It defines `kexec_purgatory`, local end label `kexec_purgatory_end`, and data symbol `kexec_purgatory_size`. The image content is included with `.incbin "arch/s390/purgatory/purgatory.ro"`.

Control flow: There is no runtime logic. Assembly-time inclusion places the purgatory binary in a read-only allocatable section aligned to eight bytes.

State and persistence: The embedded byte array persists in the kernel image and is copied into kexec/purgatory memory when building a new kernel image.

Dependencies and integration points: It depends on the `purgatory.ro` build artifact and Linux linkage macros. It integrates with s390 kexec image preparation code that reads these symbols.

Risks and test signals: The incbin path must match the Makefile output location, and size calculation must stay correct for loaders. Tests include successful kernel build, symbol inspection, and kexec image loading that validates the embedded purgatory size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/kexec-purgatory.S -->

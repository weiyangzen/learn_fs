<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/kexec-purgatory.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/purgatory/kexec-purgatory.S

Purpose: embeds the linked purgatory trampoline binary into the kernel as read-only data and exports its address and size.

Important APIs/types/functions: global symbols `kexec_purgatory` and `kexec_purgatory_size`; `.incbin "arch/powerpc/purgatory/purgatory.ro"` includes the built blob.

Control flow: there is no executable logic in this wrapper. It lays out the blob at 8-byte alignment, records the end label, and emits a quad containing blob length.

State and persistence: the embedded blob persists in kernel rodata and is later copied/relocated by kexec setup.

Dependencies and integration points: depends on the Makefile producing `purgatory.ro`. Kexec code consumes the exported symbols to locate and size the blob.

Risks: incorrect alignment or size computation would corrupt kexec payload preparation. The include path is build-layout-sensitive.

Test signals: link success, exported symbol presence, nonzero size, and successful kexec image loading validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/purgatory/kexec-purgatory.S -->

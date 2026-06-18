<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/processor.h -->
# sources/distributed-fs/ceph-client/include/vdso/processor.h

Purpose: wraps architecture-specific vDSO processor helpers for non-assembly code.

Important APIs and types: the header itself defines no public function; it includes `asm/vdso/processor.h`, which typically provides `cpu_relax()` or related low-level helpers.

Control flow: vDSO spin-wait loops such as sequence-counter readers use arch processor helpers to wait efficiently.

State and persistence: no state.

Dependencies and integration points: depends on architecture vDSO processor headers and is used by `vdso/helpers.h`.

Risks and test signals: risks are missing arch implementations or unsafe inclusion in assembly. Test vDSO builds for every architecture and reader spin behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/processor.h -->

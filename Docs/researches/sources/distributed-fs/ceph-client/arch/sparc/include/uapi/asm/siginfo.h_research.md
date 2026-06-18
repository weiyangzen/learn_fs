<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/siginfo.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/siginfo.h

Purpose: SPARC siginfo customizations layered on generic siginfo.

Important APIs and control flow: for 64-bit SPARC, `__ARCH_SI_BAND_T` is `int`; generic siginfo definitions are included; `SI_NOINFO` is defined as 32767.

State, dependencies, and risks: state is signal metadata delivered to userspace. Dependencies include generic siginfo layout and SPARC signal delivery. Risks are siginfo field-size mismatch and value compatibility for no-info signals. Test signals are realtime signal delivery, `sigwaitinfo`, ptrace signal injection, and 32-bit/64-bit siginfo layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/siginfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sigcontext.h

Purpose: Placeholder UAPI header retained for include compatibility.

Important APIs and control flow: defines no structures or constants; comments note it must not be empty enough for patch tooling to delete it.

State, dependencies, and risks: no runtime state. Dependencies are userspace and kernel headers that include `asm/sigcontext.h`. Risk is removal breaking source compatibility even though signal context layouts live elsewhere. Test signals are userspace header builds including signal headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sigcontext.h -->

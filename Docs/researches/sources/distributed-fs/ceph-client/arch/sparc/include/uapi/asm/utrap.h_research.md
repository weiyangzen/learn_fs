<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/utrap.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/utrap.h

Purpose: Defines SPARC64 user-trap type numbers and handler types.

Important APIs and control flow: constants enumerate instruction, data, FP, tag, division, alignment, privileged-action, async data, and trap-instruction user trap slots. `UTH_NOCHANGE` denotes no handler change. C consumers get `utrap_entry_t` and `utrap_handler_t` typedefs.

State, dependencies, and risks: state is userspace trap handler registration and dispatch. Dependencies are SPARC64 user-trap syscall/trap support. Risks include stable numbering for applications using user-level trap handlers and pointer compatibility. Test signals are user trap registration, illegal/divide/alignment trap handling, and handler no-change semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/utrap.h -->

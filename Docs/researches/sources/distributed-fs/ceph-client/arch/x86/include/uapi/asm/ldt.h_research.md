<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ldt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ldt.h

Purpose: Defines the userspace ABI for the legacy `modify_ldt` syscall, including LDT capacity and user descriptor layout.

Important APIs/types/functions: `LDT_ENTRIES`, `LDT_ENTRY_SIZE`, `struct user_desc`, and `MODIFY_LDT_CONTENTS_*`.

Control flow: Userspace passes `user_desc` to `modify_ldt`; kernel validates fields and installs or reads LDT descriptors. On 64-bit, base/limit and many segment choices are constrained, and `lm` must be treated carefully for 32-bit callers.

State and persistence behavior: LDT entries persist in per-mm or per-task descriptor tables until replaced or process exit. The header itself owns no state.

Dependencies and integration points: Integrates with segmentation, TLS/compat tasks, ptrace-like process setup, DOSEMU/Wine-style users, and syscall entry restrictions.

Risks and test signals: Risks include 32-bit user initialization of the 64-bit `lm` bit, descriptor privilege mistakes, and syscall compatibility regressions. Test `modify_ldt` selftests, i386 compatibility, Wine/DOSEMU workloads, and 64-bit syscall behavior with unusual segment descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ldt.h -->

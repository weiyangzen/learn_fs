# sources/distributed-fs/ceph-client/arch/x86/include/asm/umip.h

Purpose: declares x86 UMIP exception fixup support.

Important APIs/types/functions: `fixup_umip_exception(struct pt_regs *regs)`.

Control flow: `CONFIG_X86_UMIP` builds call into the real fixup implementation; non-UMIP builds inline-return `false`.

State/persistence: no state in the header; the implementation operates on trap register state.

Dependencies/integration: depends on `pt_regs` and UMIP trap handling for privileged instruction emulation or signal delivery.

Risks/test signals: wrong return value can cause incorrect handling of user-mode SGDT/SIDT/SLDT/SMSW/STR faults. Test with UMIP enabled/disabled, user-space privileged instruction probes, signal delivery, and virtualization/compat mode coverage.

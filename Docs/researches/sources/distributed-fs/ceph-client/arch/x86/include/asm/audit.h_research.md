
# sources/distributed-fs/ceph-client/arch/x86/include/asm/audit.h

Purpose: x86 audit syscall classification declarations, focused on IA32 compatibility syscall classes.

Important APIs and control flow: declares `ia32_classify_syscall()` and class arrays for directory, write, read, chattr, and signal audit categories. Runtime control flow lives in audit/syscall code that indexes these arrays to map syscall numbers to audit classes.

State, dependencies, and risks: state is the external classification arrays. Dependencies include audit core and IA32 syscall numbering. Risks include syscall table drift, class-array size mismatches, and missing x32/compat distinctions. Test signals are audit rule tests under IA32 emulation and syscall-class regression tests.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/smap.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/smap.h

Purpose: defines Supervisor Mode Access Prevention helpers for toggling user-memory access from kernel mode. Important macros/functions include `ASM_STAC`, `ASM_CLAC`, `stac()`, `clac()`, `__uaccess_begin()`, `__uaccess_end()`, and masked user-access helpers depending on config and CPU feature.

Control flow: uaccess code opens a small window with STAC before touching user memory and closes it with CLAC afterward. Alternative patching removes or changes instructions when SMAP is absent. State is the AC flag in RFLAGS and CPU feature alternatives.

Dependencies include CPU feature detection, alternatives, uaccess routines, exception entry, and objtool/asm annotations. Risks include leaving AC set, missing STAC before user access, using helpers in NMI/entry contexts incorrectly, and mismatched alternatives. Test signals include hardened usercopy, SMAP fault tests, uaccess selftests, fault injection, and objtool validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/smap.h -->

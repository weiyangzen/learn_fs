<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/boot.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/boot.h

Purpose: Exposes legacy x86 boot video mode constants used by setup/bootloader interfaces.

Important APIs/types/functions: `NORMAL_VGA`, `EXTENDED_VGA`, and `ASK_VGA`.

Control flow: Bootloaders or setup code pass these constants in boot parameters to request standard, extended, or interactive VGA mode selection.

State and persistence behavior: No runtime state. Values persist only as boot protocol constants.

Dependencies and integration points: Integrates with x86 boot protocol, setup header video mode fields, and early console/video initialization.

Risks and test signals: Risks are minimal but include stale bootloader assumptions. Test booting with normal, extended, and ask video mode options on BIOS-style x86 boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/boot.h -->

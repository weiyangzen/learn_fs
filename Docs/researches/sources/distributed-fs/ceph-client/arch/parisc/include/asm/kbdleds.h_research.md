# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kbdleds.h

Purpose: declares PA-RISC keyboard LED defaults or hooks for console keyboard support.

Important APIs/types/functions: exports keyboard LED constants/macros consumed by generic keyboard code.

Control flow: keyboard/VT code reads the architecture default when initializing LED state.

State and persistence: LED state is ultimately device state; the header stores no runtime state. Dependencies and integration: integrates with console keyboard and legacy input support.

Risks and test signals: low risk; wrong defaults only affect initial keyboard LED behavior. Test with keyboard/VT build coverage and boot on systems with legacy keyboard hardware.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.

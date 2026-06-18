<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/call_o32.S -->
## sources/distributed-fs/ceph-client/arch/mips/fw/lib/call_o32.S

**Purpose:** Provides `call_o32`, an assembly dispatcher that lets 64-bit or N32 kernels call 32-bit O32 firmware routines.

**Important APIs/types/functions:** `call_o32` accepts a firmware function pointer in `a0`, optional alternate stack in `a1`, first six firmware arguments in `a2-a7`, and remaining arguments on the caller stack. It preserves static registers, `gp`, `fp`, and returns firmware `v0`.

**Control flow:** The dispatcher saves registers, optionally switches to a supplied O32 stack, truncates/places arguments into an O32 argument frame, calls the firmware function with `jalr`, restores the original stack and saved registers, and returns.

**State, dependencies, integration:** Depends on MIPS assembler macros from `asm.h`. It is used by PROM paths that cannot pass 64-bit kernel stack pointers to 32-bit firmware.

**Risks and test signals:** It supports up to 32 O32 arguments and requires called firmware to restore `sp`/`ra` as expected. Test with stack and non-stack calls, argument truncation, static register preservation, and firmware pointers in addressable KSEG/KUSEG regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/call_o32.S -->

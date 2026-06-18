# sources/distributed-fs/ceph-client/arch/parisc/include/asm/runway.h

Purpose: defines small register offsets for PA-RISC Runway bus status/debug access.

Important APIs/types/functions: exports `RUNWAY_STATUS` and `RUNWAY_DEBUG`.

Control flow: platform diagnostic code reads or writes these offsets relative to Runway bus control blocks.

State and persistence: accessed registers are hardware state; this header stores none. Dependencies and integration: used by Runway chipset/platform support.

Risks and test signals: incorrect offsets affect low-level hardware diagnostics. Test with build coverage and hardware readback on Runway systems.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.

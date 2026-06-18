<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/contregs.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/contregs.h

## Purpose
This header defines Sun-3/Sun m68k control-space register addresses for MMU, cache, DVMA, bus error, LEDs, VME, and boot SCC access.

## Important APIs, Types, And Functions
- `AC_*` constants identify control address spaces such as IDPROM, pagemap, segment map, context, system enable, bus error, cache tags/data, DVMA map, VME vector, and boot SCC.
- `AC_M_*` constants identify MMU register offsets such as processor control, context table/root pointers, context register, synchronous/asynchronous fault registers, reset, and TLB replacement controls.

## Control Flow
Low-level Sun MMU and platform code uses these constants in special address-space access instructions or control-space mappings. No functions are defined here.

## State And Persistence Behavior
The constants reference persistent processor/platform control registers. Reads observe MMU/cache/fault state; writes can change contexts, mappings, cache state, reset behavior, or VME handling.

## Dependencies And Integration Points
It integrates with Sun3/Sun3x MMU, cache, bus error, DVMA, LED, VME, and serial bootstrap code.

## Risks And Edge Cases
Control-space constants are privileged hardware contracts. Writing wrong registers can corrupt address translation or reset the system. Several offsets are CPU-model-specific and comments encode model applicability.

## Test Signals
Sun3/Sun3x boot, MMU context switching, page/segment map operations, bus error reporting, DVMA mapping, cache tag/data access, VME interrupts, and LED control validate use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/contregs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_32.h

## Purpose
This header implements SPARC32 floppy-controller glue, including DMA, AUXIO motor/select control, and platform quirks.

## Important APIs, Types, and Functions
It defines architecture hooks expected by the generic floppy driver: DMA setup/teardown, virtual DMA behavior, controller I/O access, interrupt/DMA limits, and AUXIO-backed drive control.

## Control Flow
The generic floppy driver calls SPARC hooks to request DMA, program transfers, control motor/select/eject lines, handle interrupts, and clean up.

## State and Persistence Behavior
State persists in floppy controller registers, AUXIO bits, DMA controller state, and driver-owned buffers.

## Dependencies and Integration Points
It integrates generic floppy code with SPARC32 AUXIO, DMA, I/O space, and interrupt handling.

## Risks
Legacy floppy timing and DMA boundaries are fragile. Wrong AUXIO bits can select/eject drives unexpectedly or fail transfers.

## Test Signals
Boot with floppy enabled, perform read/write/format/eject tests, and exercise DMA boundary/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_32.h -->

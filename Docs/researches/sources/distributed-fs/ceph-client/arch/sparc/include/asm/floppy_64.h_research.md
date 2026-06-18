<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_64.h

## Purpose
This header implements SPARC64 floppy-controller integration for the generic floppy driver.

## Important APIs, Types, and Functions
It defines SPARC64-specific controller access, DMA or pseudo-DMA handling, interrupt setup, drive control, and platform quirks needed by generic floppy code.

## Control Flow
Generic floppy operations route through these hooks for register I/O, DMA movement, motor control, and interrupt completion.

## State and Persistence Behavior
Runtime state resides in controller hardware, DMA mappings, AUXIO/PCIO bits, and driver buffers.

## Dependencies and Integration Points
It integrates generic floppy support with SPARC64 I/O, AUXIO, EBus/PCI platform plumbing, and DMA mapping.

## Risks
Large inline architecture hooks make register ordering, DMA mapping, and platform detection error-prone. Mistakes can hang the controller or corrupt buffers.

## Test Signals
Run floppy probe and media read/write tests on SPARC64 systems with floppy hardware; enable DMA debugging and interrupt tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/floppy_64.h -->

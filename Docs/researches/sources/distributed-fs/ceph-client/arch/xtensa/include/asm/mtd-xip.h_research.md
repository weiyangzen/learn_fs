<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mtd-xip.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mtd-xip.h

## Purpose
Provides Xtensa hooks used by MTD execute-in-place code while running directly from flash.

## Important APIs, Types, And Functions
Defines `xip_irqpending`, `xip_currtime`, `xip_elapsed_since`, and `xip_cpu_idle`.

## Control Flow
Macros read interrupt pending/enabled and cycle counter special registers, compute elapsed time by scaled cycle difference, and idle with `waiti 0`.

## State And Persistence
No state beyond CPU special registers.

## Dependencies And Integration Points
Depends on `xtensa_get_sr`, interrupt register definitions, cycle counter availability, and MTD XIP polling/idle code.

## Risks And Edge Cases
Elapsed-time scaling assumes cycle count up to about 1 GHz as commented. `waiti 0` must be safe while executing from XIP flash and waiting for interrupts.

## Test Signals
Build and boot XIP kernels, exercise MTD XIP erase/write wait paths, and verify interrupt wakeups during XIP operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mtd-xip.h -->

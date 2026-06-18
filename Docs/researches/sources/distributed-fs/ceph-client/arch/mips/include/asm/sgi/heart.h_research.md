# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/heart.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/heart.h

### Purpose
`sgi/heart.h` defines the SGI IP30 HEART system controller register map, timer constants, memory-bank layout, interrupt priorities/vectors, error/status masks, and raw 64-bit register access aliases.

### Important APIs, Types, And Functions
Key type is `struct ip30_heart_regs`, mapping mode, SDRAM, memory config, flow control, status/error registers, interrupt mask/status/cause, counter/compare/trigger, CPU ID, and sync registers. Important macros include `HEART_MEMORY_BANKS`, `HEART_MAX_CPUS`, `HEART_XKPHYS_BASE`, `HEART_NS_PER_CYCLE`, `HEART_CYCLES_PER_SEC`, `HEART_*` masks, `HM_*` mode bits, memory refresh/config fields, status/cause fields, `HEART_NUM_IRQS`, priority masks `HEART_L*_INT_MASK`, interrupt vector numbers, external `heart_regs`, and `heart_read`/`heart_write`.

### Control Flow
Platform code maps `heart_regs`, reads/writes 64-bit registers, configures memory controller and interrupts, uses HEART count/compare for timing, and clears/sets interrupt status through dedicated registers.

### State, Persistence, Dependencies, And Integration
State is IP30 system controller MMIO: memory configuration, error latches, interrupt masks/status, timer count/compare, and reset/mode bits. Dependencies include Linux types/time and raw 64-bit I/O helpers. Integration covers IP30 memory discovery, interrupt controller, timer, reset/error handling, and Xtalk/Bridge error propagation.

### Risks
All registers are 64-bit-wide but memory config requires 32-bit reads for useful bank values. Many fields are marked not fully understood, so changing masks can affect hardware behavior. Incorrect interrupt priority masks can route errors to wrong CPU pins.

### Test Signals
Boot IP30, validate memory bank detection, timer frequency, IRQ routing across priority levels, bus/memory error handling, and 32-bit versus 64-bit mem_cfg access behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/heart.h -->

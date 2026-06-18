## sources/distributed-fs/ceph-client/arch/s390/include/asm/timex.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/timex.h` is a s390 TOD clock and timer
primitives in the s390 ceph-client Linux source snapshot. It has 289 lines and 6798 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
TOD/PTFF structures, inline STCK/STCKF/STCKE helpers, clock comparator programming, CPU timer setup,
and early time initialization declarations
Important macros/constants: `_ASM_S390_TIMEX_H`, `TOD_UNIX_EPOCH`, `PTFF_QAF`, `PTFF_QTO`, `PTFF_QSI`, `PTFF_QPT`, `PTFF_QUI`, `PTFF_ATO`, `PTFF_STO`, `PTFF_SFS`, `PTFF_SGS`, `ptff(ptff_block, len, func)`, `CLOCK_TICK_RATE`, `get_cycles`.
Important types/layouts: `tod_clock`, `ptff_qto`, `ptff_qui`, `addrtype`.
Important declarations or inline helpers: `volatile`, `CC_TRANSFORM`, `clock_comparator_work`, `time_early_init`, `get_phys_clock`, `init_cpu_timer`, `set_tod_clock`, `store_tod_clock_ext_cc`, `store_tod_clock_ext`, `set_clock_comparator`, `set_tod_programmable_field`, `ptff_query`, `local_tick_disable`, `local_tick_enable`, `get_tod_clock`, `get_tod_clock_fast`, `__get_tod_clock_monotonic`, `get_tod_clock_monotonic`, `get_cycles`, `tod_to_ns`; plus 3 more.

### Control Flow
The header is mostly inline fast-path code: callers enter small assembly sequences, condition-code
extraction converts hardware results into C values, and fallback or wait loops are selected through
architecture facilities and alternative patching.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
timekeeping, sched clock, vDSO time, CPU idle/tick handling, and machine facility detection. Direct
include dependencies detected here: `linux/preempt.h`, `linux/time64.h`, `asm/lowcore.h`,
`asm/machine.h`, `asm/asm.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for timekeeping, sched clock, vDSO time, CPU
idle/tick handling, and machine facility detection. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
wrong epoch conversion, mask handling, or comparator programming causes time jumps or lost timer
interrupts

### Test Signals
clocksource tests, vDSO time tests, suspend/idle tick tests, and STCK/STCKF facility coverage

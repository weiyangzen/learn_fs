# sources/distributed-fs/ceph-client/arch/x86/include/asm/numachip/numachip_csr.h

## Purpose
Defines Numascale NumaConnect CSR address constants and inline read/write helpers for local CSR spaces on first- and second-generation Numachip systems.

## Important APIs, Types, And Functions
Defines `CSR_NODE_SHIFT`, `CSR_NODE_BITS()`, `CSR_NODE_MASK`, `CSR_OFFSET_MASK`, CSR offsets such as `CSR_G0_NODE_IDS` and `CSR_G3_EXT_IRQ_GEN`, first-generation `NUMACHIP_LCSR_*` constants, `lcsr_address()`, `read_lcsr()`, `write_lcsr()`, second-generation `NUMACHIP2_LCSR_*`, timer/APIC offsets, `numachip2_lcsr_address()`, `numachip2_read32_lcsr()`, `numachip2_read64_lcsr()`, `numachip2_write32_lcsr()`, `numachip2_write64_lcsr()`, and `numachip2_timer()`.

## Control Flow
Callers compute local CSR virtual addresses by ORing fixed physical windows with offset masks, then perform endian-swapped 32-bit accesses for original Numachip or native 32/64-bit MMIO accesses for Numachip2. `numachip2_timer()` selects per-CPU timer offset using CPU ID modulo 48.

## State And Persistence
State is hardware CSR/MMIO state. Writes persist in platform registers until changed or reset.

## Dependencies And Integration Points
Depends on SMP CPU IDs, I/O accessors, byte swapping, `__va()`, and platform mapping assumptions. It integrates with Numachip interrupt, timer, APIC, and node discovery code.

## Risks And Edge Cases
Physical windows and PMD alignment assumptions are platform-specific. Endianness swapping must match hardware. The CPU modulo timer calculation assumes fixed per-node timer layout.

## Test Signals
Boot on Numachip/Numachip2 hardware, CSR read sanity, timer interrupt delivery, external IRQ generation, and CPU hotplug on high-node systems are useful.

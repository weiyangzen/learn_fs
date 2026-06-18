<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmio.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmio.h

## Purpose
Defines raw and endian-converting MMIO accessors plus relaxed/ordered read/write wrappers.

## Important APIs, Types, And Functions
functions/prototypes `__raw_writeb`, `__raw_writew`, `__raw_writel`, `__raw_writeq`, `__raw_readb`, `__raw_readw`, `__raw_readl`, `__raw_readq`; macros/constants `_ASM_RISCV_MMIO_H`, `__raw_writeb`, `__raw_writew`, `__raw_writel`, `__raw_writeq`, `__raw_readb`, `__raw_readw`, `__raw_readl`, `__raw_readq`, `readb_cpu(c) ({ u8 __r = __raw_readb(c); __r; })`, `readw_cpu(c) ({ u16 __r = le16_to_cpu((__force __le16)__raw_readw(c)); __r; })`, `readl_cpu(c) ({ u32 __r = le32_to_cpu((__force __le32)__raw_readl(c)); __r; })`, `writeb_cpu(v, c) ((void)__raw_writeb((v), (c)))`, `writew_cpu(v, c) ((void)__raw_writew((__force u16)cpu_to_le16(v), (c)))`, plus 27 more.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `asm/fence.h`, `asm/mmiowb.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 152 lines, 5292 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmio.h -->

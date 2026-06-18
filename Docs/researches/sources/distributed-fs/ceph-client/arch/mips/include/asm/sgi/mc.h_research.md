# sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/mc.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/mc.h

### Purpose
`sgi/mc.h` maps the SGI IP20/IP22/IP26/IP28 memory controller registers and defines control, parity/error, GIO DMA, memory configuration, EEPROM, watchdog, RPSS, and DMA operation bit fields.

### Important APIs, Types, And Functions
The key type is `struct sgimc_regs`. Important macros cover `SGIMC_CCTRL0_*`, `SGIMC_CCTRL1_*`, `SGIMC_SYSID_*`, EEPROM bits, `SGIMC_GIOPAR_*`, memory config bits, CPU/GIO error status bits, DMA registers, base address `SGIMC_BASE`, memory segment base/size constants, global `sgimc`, and `sgimc_init`.

### Control Flow
Platform code maps `sgimc`, configures memory refresh/control, probes memory banks, handles parity/bus errors by reading error/status registers, controls GIO DMA translation and DMA operations, and uses the watchdog/RPSS counters as needed.

### State, Persistence, Dependencies, And Integration
State is memory-controller MMIO, EEPROM bits, memory bank configuration, parity/error latches, DMA TLB entries, DMA transfer state, and global mapped pointer. Integration includes memory sizing, GIO/EISA/HPC endianness, bus-error handling, DMA, watchdog, and platform initialization.

### Risks
Control bits can reset hardware, alter endianness, enable PROM writes, or affect memory refresh. Mis-decoding bank config can expose absent memory or miss RAM. DMA TLB and transfer registers require strict ordering.

### Test Signals
Boot supported SGI systems, verify memory map against physical RAM, test parity/bus-error reporting, GIO/EISA/HPC devices, DMA transfers, EEPROM reads, and watchdog/reset paths under controlled conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sgi/mc.h -->

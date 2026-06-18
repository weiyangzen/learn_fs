# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_polaris.h

This header provides the Polaris platform's core memory and I/O map. It defines sparse/dense memory, sparse/dense I/O, config, and IACK base addresses, a few dense config vendor/device/status register aliases, and a minimal Polaris machine-check system-data structure.

Runtime APIs are `polaris_ioportmap`, `polaris_ioremap`, `polaris_is_ioaddr`, and `polaris_is_mmio`. The header declares all read/write and I/O operations trivial through `io_trivial.h`, with `__IO_PREFIX=polaris`.

State is the mapped chipset address space and any external machine-check data. Integration is the compile-time chipset branch in `asm/io.h`. Risks are low compared with sparse-chipset headers, but base-address constants and MMIO-vs-port classification must match hardware. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.

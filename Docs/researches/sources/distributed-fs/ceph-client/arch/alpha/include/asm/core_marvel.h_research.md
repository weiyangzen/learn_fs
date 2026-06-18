# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_marvel.h

This header defines EV7 Marvel/IO7 platform addressing and register structures. It covers EV7 CSR address construction, IO7 port/hose physical and kernel addresses, IRQ vector sizing for up to 32 PIDs, IO7 window/control unions, `io7_port` and `io7` topology structures, and IACK/DAC constants.

Important APIs include external `marvel_ioread8`, `marvel_iowrite8`, `marvel_ioremap`, `marvel_iounmap`, `marvel_ioportmap`, `marvel_is_mmio`, inline 16-bit helpers using `__kernel_ldwu/stw`, and `marvel_is_ioaddr`. It sets `__IO_PREFIX=marvel`, with direct MMIO read/write operations but non-trivial byte/word port I/O.

State is IO7 topology, per-port CSR pointers, PCI window registers, and Marvel interrupt routing. Integration is through generic Alpha I/O dispatch, PCI hose discovery, AGP port handling, and EV7 error/interrupt code. Risks include large multi-processor/hose address encodings, 49-bit DAC offset assumptions, port 7 CSR handling, and mixing direct kernel addresses with remapped resources. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.

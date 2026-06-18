# sources/distributed-fs/ceph-client/include/soc/fsl/qe/immap_qe.h

Purpose: defines the QUICC Engine internal memory map as packed C structs matching the SoC MMIO layout.

Important APIs and types: `QE_IMMAP_SIZE` covers the 1 MiB QE block. Structs model I-RAM, interrupt controller, communications processor, mux, timers, BRG, SPI, SI, SI RAM routing tables, USB, MCC, UCC slow/fast register blocks, generic UCC slots, UPC controllers, SDMA, debug space, RISC special registers, and the top-level `struct qe_immap`. `extern struct qe_immap __iomem *qe_immr` exposes the mapped base.

Control flow: QE platform code maps the IMMR/QE region into `qe_immr`, then drivers access typed substructures for register programming, microcode upload, timers, UCC protocols, SDMA, and routing tables.

State and persistence: all represented fields are live MMIO/hardware state. Some MURAM contents hold parameter RAM or buffer descriptors during runtime but are not persistent across reset.

Dependencies and integration points: gated by `__KERNEL__`, depends on big-endian MMIO types and `asm/io.h`, and is used by QE, CPM, UCC, TDM, USB, Ethernet, serial, and SDMA drivers.

Risks and test signals: risks include struct packing/offset drift, SoC variant register differences, direct MMIO access without ordering, and mismatched endian accessors. Test register offset assertions where available, QE boot/probe, UCC fast/slow drivers, microcode upload, MURAM access, and compile coverage on PowerPC QE SoCs.

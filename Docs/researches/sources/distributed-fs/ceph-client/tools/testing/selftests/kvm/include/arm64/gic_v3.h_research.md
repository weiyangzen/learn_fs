<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3.h

Purpose: this arm64 helper header centralizes GICv3, redistributor, ITS, LPI/VLPI, and CPU-interface register offsets and bitfield definitions used by KVM selftests.

Important APIs, types, and functions: it defines distributor offsets (`GICD_*`), redistributor offsets (`GICR_*`), ITS offsets (`GITS_*`), register size constants, page-size encodings, baser cacheability/shareability helpers, LPI property bits, ITS command opcodes and error numbers, and CPU interface fields such as `ICC_CTLR_EL1_*`, `ICC_SRE_EL1_*`, `ICC_SGI1R_*`, and `ICC_IAR1_EL1_SPURIOUS`. Macros like `GICD_TYPER_SPIS()`, `GICD_TYPER_ESPIS()`, `GICR_TYPER_NR_PPIS()`, `GITS_BASER_ENTRY_SIZE()`, and address conversion helpers decode hardware-emulated register fields.

Control flow: this file has no executable control flow; it supplies compile-time constants consumed by guest helpers, VGIC setup helpers, and tests that read/write KVM VGIC device attributes.

State, persistence, and dependencies: no state. It depends on Linux bit macros such as `GENMASK_ULL` and is included by GIC library/test code that performs actual MMIO/sysreg accesses.

Risks and edge cases: correctness depends on matching the Arm GIC architecture and KVM's emulated register layout. Address-field helpers for 52-bit ITS BASER values and GICR/GITS table cacheability fields are easy to misuse. Some definitions cover GICv4/VLPI even when tests run only GICv3 paths.

Test signals: downstream tests validate these definitions indirectly by successfully initializing VGIC/ITS, programming LPI tables, reading GICR_TYPER, manipulating priorities/groups, and exercising sysreg attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3.h -->

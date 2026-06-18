# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/Kconfig

Purpose: Defines kernel configuration symbols for the Marvell OcteonTX2 RVU networking driver family. It controls whether mailbox support, Admin Function, PF, VF, NDC dynamic caching disable, and RVU e-switch support are built.

Important APIs/types/functions: Kconfig symbols are `OCTEONTX2_MBOX`, `OCTEONTX2_AF`, `NDC_DIS_DYNAMIC_CACHING`, `OCTEONTX2_PF`, `OCTEONTX2_VF`, and `RVU_ESWITCH`. `OCTEONTX2_AF` selects mailbox and devlink support and depends on PCI, optional PTP clock support, and ARM64 or 64-bit compile testing. `OCTEONTX2_PF` selects mailbox, devlink, page pool, DIMLIB, and optionally AES crypto for MACsec. `OCTEONTX2_VF` depends on PF support. `RVU_ESWITCH` depends on PF support and defaults to module.

Control flow and integration: These symbols drive Makefile object inclusion and driver availability. Enabling AF builds the resource manager that other RVU functions rely on. Enabling PF builds the host NIC PF; VF support is gated behind PF because the VF driver shares PF-side infrastructure. The dynamic caching option changes AF behavior by disabling caching and locking down context entries.

State and persistence: Kconfig choices persist in the kernel build configuration and shape compiled modules. There is no runtime state here.

Dependencies: Integrates with Linux Kconfig, PCI, devlink, PTP, page pool, DIMLIB, MACsec, and architecture/compile-test constraints.

Risks: Dependency mistakes can produce unresolved symbols or unavailable drivers for supported systems. `RVU_ESWITCH` defaulting to `m` can surprise minimal builds. `NDC_DIS_DYNAMIC_CACHING` has performance and behavior implications because it alters hardware context caching policy.

Test signals: Matrix builds for AF/PF/VF/e-switch combinations, ARM64 and COMPILE_TEST builds, MACsec enabled/disabled builds, and module dependency checks should verify this file.

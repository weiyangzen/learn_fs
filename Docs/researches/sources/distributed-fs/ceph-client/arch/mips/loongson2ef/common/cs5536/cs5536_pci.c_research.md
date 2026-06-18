<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_pci.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_pci.c

Purpose: Provides the CS5536 virtual PCI config-space dispatcher. It maps a CS5536 multifunction PCI function number to a per-function VSM read/write implementation that emulates config accesses with MSR operations.

Important APIs/types/functions: `cs5536_pci_conf_write4(function, reg, value)` validates a 32-bit aligned config offset and invokes `pci_isa/ide/acc/ohci/ehci_write_reg`. `cs5536_pci_conf_read4(function, reg)` validates offsets, returns `0xffffffff` for out-of-range high config reads, and calls the matching read hook.

Control flow: Static arrays indexed by local function enum hold function pointers. The reserved function intentionally maps to `NULL`, so accesses become no-ops or zero reads. Invalid function numbers and unaligned registers are rejected before dispatch.

State and persistence: This file stores no hardware state itself; it funnels operations to VSM modules that update CS5536 MSRs.

Dependencies and integration: Included by the Loongson2EF PCI ops path when firmware or config cycles target the CS5536 device. Depends on `cs5536_vsm.h` declarations for each function backend.

Risks: Function index values must match the hardware-visible multifunction layout. Returning zero for valid but unimplemented reads differs from real PCI config all-ones behavior and can hide errors.

Test signals: Config dword reads for each CS5536 function should hit the proper backend; unaligned and invalid accesses should not mutate MSRs; reads beyond 0x100 should return all ones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_pci.c -->

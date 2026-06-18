# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_acc.c

Purpose: virtualizes PCI configuration space for the CS5536 ACC function using MSR-backed hardware state.

Important APIs/functions: `pci_acc_write_reg` and `pci_acc_read_reg`.

Control flow: writes handle PCI command bus mastering through `GLIU_PAE`, parity status clearing through `SB_ERROR`, BAR probing/allocation through soft BAR flag and `GLIU_IOD_BM1`, and interrupt routing through `PIC_YSEL_LOW`. Reads synthesize vendor/device, command/status, class revision, BAR, subsystem, ROM, capability, and interrupt-line values.

State and persistence: hardware MSRs hold BAR, error, bus-master, and interrupt-routing state; soft BAR probe flags are stored in `GLCP_SOFT_COM`.

Dependencies and integration: called by CS5536 PCI config virtualization layer; depends on `cs5536.h` and `cs5536_pci.h` macros and `_rdmsr/_wrmsr`.

Risks: BAR probing uses side-effect soft flags that are cleared on read. Incorrect MSR bit packing breaks IO decoding or interrupts.

Test signals: PCI config-space reads/writes for ACC, BAR sizing, bus-master enable toggles, parity clear behavior, and interrupt line reporting.

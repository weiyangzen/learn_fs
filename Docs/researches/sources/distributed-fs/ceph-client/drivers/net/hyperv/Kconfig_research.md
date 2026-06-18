# sources/distributed-fs/ceph-client/drivers/net/hyperv/Kconfig

### Purpose
This Kconfig entry exposes `CONFIG_HYPERV_NET`, the Microsoft Hyper-V virtual network driver, as a tristate option. It is the build-time gate for the `hv_netvsc` module or built-in driver.

### Important APIs, Types, And Functions
There are no C APIs in this file. The important symbol is `HYPERV_NET`. It depends on `HYPERV_VMBUS` and selects `UCS2_STRING` and `NLS`, which are required by the broader Hyper-V/RNDIS support stack.

### Control Flow
Kconfig evaluation enables this option only when Hyper-V VMBus support is available. If selected as built-in or module, the Makefile in the same directory builds `hv_netvsc.o`.

### State And Persistence Behavior
The file contributes only kernel configuration state. It has no runtime persistence, but the selected value determines whether the Hyper-V network driver is present in the built kernel or modules.

### Dependencies And Integration Points
The direct integration point is the kernel Kconfig system and the local Makefile. Runtime driver code depends on VMBus, so the `depends on HYPERV_VMBUS` relationship is the critical safety gate.

### Risks
The main risk is dependency drift: if runtime code adds new library or subsystem requirements, this Kconfig must select or depend on them. A missing dependency would show up as build failures when `HYPERV_NET=m/y`.

### Test Signals
Build matrix checks should include `HYPERV_NET=n`, `m`, and `y` with `HYPERV_VMBUS` enabled, and ensure the option is not offered or cannot be selected without VMBus support.

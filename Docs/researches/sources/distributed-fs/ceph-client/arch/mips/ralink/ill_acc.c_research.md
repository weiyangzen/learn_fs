## sources/distributed-fs/ceph-client/arch/mips/ralink/ill_acc.c

### Purpose
This file installs an illegal memory-access interrupt handler for RT305x-class Ralink memory controllers. It reports which bus master made an invalid read/write and clears the interrupt.

### Important APIs, Types, And Functions
`ill_acc_ids[]` names hardware requesters. `ill_acc_irq_handler()` reads illegal access address/type registers, decodes write/read, source ID, offset, and length, logs an error, and clears status. `ill_acc_of_setup()` locates the `"ralink,rt3050-memc"` node/platform device, maps IRQ, requests it, clears pending status, and logs registration.

### Control Flow
At `arch_initcall()`, setup skips RT5350, finds the memory-controller node, obtains the platform device and IRQ, installs the handler, and clears `ILL_INT_STATUS`. Interrupts later decode and clear each illegal access.

### State, Persistence, And Dependencies
Persistent state is the requested IRQ and enabled memory-controller interrupt status. Dependencies include Ralink memc register helpers, OF platform lookup, IRQ mapping, and RT305x compatibility.

### Integration Points
Selected by `RALINK_ILL_ACC` for SOC_RT305X and complements platform diagnostics.

### Risks
If `of_find_device_by_node()` succeeds and `request_irq()` succeeds, the device reference is intentionally retained; failure paths must release it. RT5350 is excluded because the driver breaks there. Logging in IRQ context can be noisy under repeated faults.

### Test Signals
Force illegal DMA/CPU accesses, confirm decoded source/address/length, and verify status clearing prevents interrupt storms.

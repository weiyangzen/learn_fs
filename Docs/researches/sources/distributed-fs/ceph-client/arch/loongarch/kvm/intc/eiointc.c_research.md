# sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/eiointc.c

Purpose: emulates the LoongArch extended I/O interrupt controller, including IOCSR register access, routing, virtual-extension registers, and migration attributes.

Important APIs, types, and functions: external entry is `eiointc_set_irq()`. Device creation/registration flows through `kvm_eiointc_create()`, `kvm_eiointc_destroy()`, `kvm_eiointc_get_attr()`, `kvm_eiointc_set_attr()`, and `kvm_loongarch_register_eiointc_device()`. Internal helpers update `sw_coreisr`, `sw_coremap`, IRQ lines, and register banks.

Control flow: asserted IRQs update `isr`, map guest IRQ to an IP line and target vCPU, update per-core ISR bitmaps, and raise/lower `INT_HWI0..INT_HWI3` parent interrupts only when the first/last child on that line changes. IOCSR reads/writes expose nodetype, ipmap, enable, bounce, coreisr, and coremap registers. Enable and coremap writes recalculate delivery. Virtual-extension registers expose feature/status bits. Attribute groups handle initialization, migration register state, and software status.

State and persistence: `struct loongarch_eiointc` persists per VM with feature/status bits, num CPU, ipmap, enable, bounce, ISR/coreISR/coremap arrays, software maps, KVM pointer, I/O devices, and spinlock. Migration state is exposed through KVM device attrs.

Dependencies and integration points: registered on the `KVM_IOCSR_BUS` at EIOINTC base ranges, receives routed interrupts from PCH-PIC/MSI paths, targets vCPUs by CPUID or vCPU ID, and injects CPU interrupt lines through `kvm_vcpu_ioctl_interrupt()`.

Risks: routing semantics depend on encoded versus bitmap CPU/IP modes. Locking must cover all bitmap updates. Partial-width IOCSR accesses use masks and offsets, so endian/size behavior must match hardware. Migration restore must call load-finished logic to rebuild software maps.

Test signals: guest irqchip driver boot, enable/disable and clear paths, coremap migration, virtual extension feature negotiation, MSI routing through PCH-PIC, and concurrent IRQ injection tests.

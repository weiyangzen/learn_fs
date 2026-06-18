# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_impl.h

**Purpose:** Private IRQ implementation header for Alpha kernel IRQ files and platform code. It declares common controller entry points, RTC IRQ number, ISA DMA initialization, i8259 chip functions, and `handle_irq()`.

**Important APIs/types/functions:** Defines `RTC_IRQ` as 8. Declares `isa_device_interrupt()`, `isa_no_iack_sc_device_interrupt()`, `srm_device_interrupt()`, `pyxis_device_interrupt()`, `init_srm_irqs()`, `init_pyxis_irqs()`, `init_rtc_irq()`, `common_init_isa_dma()`, `i8259a_enable_irq()`, `i8259a_disable_irq()`, `i8259a_mask_and_ack_irq()`, `i8259a_irq_type`, `init_i8259a_irqs()`, and `handle_irq()`.

**Control flow:** No runtime code; the declarations allow system-specific `sys_*.c` files and controller backends to wire machine vectors and IRQ chips together consistently.

**State and persistence behavior:** None. It exposes functions that mutate IRQ controller state elsewhere.

**Dependencies and integration points:** Includes generic interrupt, IRQ, and profile headers. Shared by `irq.c`, `irq_alpha.c`, `irq_i8259.c`, `irq_pyxis.c`, `irq_srm.c`, and many Alpha system platform files.

**Risks:** Any signature mismatch here breaks cross-file builds. `RTC_IRQ` is baked into Alpha timer interrupt handling and must match PAL vector assumptions. Because it is private, adding declarations here without corresponding build coverage can leave some platform configs broken.

**Test signals:** Compile all Alpha platform configurations, especially those using SRM-only, Pyxis, i8259, and custom system IRQ handlers. Confirm no duplicate or missing declarations as generic IRQ APIs evolve.

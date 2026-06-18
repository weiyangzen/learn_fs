# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_srm.c

**Purpose:** Provides SRM PALcode-managed interrupt support for Alpha systems that let firmware handle interrupt masking. It defines an IRQ chip using `cserve_ena/dis`, initializes SRM IRQ descriptors, and converts SRM vectors to Linux IRQ numbers.

**Important APIs/types/functions:** Exposes `srm_irq_lock`, `init_srm_irqs()`, and `srm_device_interrupt()`. Internal helpers are `srm_enable_irq()`, `srm_disable_irq()`, and `srm_irq_type`.

**Control flow:** `init_srm_irqs(max, ignore_mask)` installs `srm_irq_type` for IRQs 16 through `max - 1`, skipping ignored IRQs below 64, and marks them level-triggered. The chip enable/disable callbacks serialize PAL console service calls with `srm_irq_lock` and pass `irq - 16` to `cserve_ena()` or `cserve_dis()`. Runtime dispatch computes `irq = (vector - 0x800) >> 4` and calls `handle_irq()`.

**State and persistence behavior:** No software mask cache; firmware/PAL owns mask state. The spinlock only serializes SMP access to PAL console service calls. No persistent data.

**Dependencies and integration points:** Depends on `cserve_ena/dis` from `head.S`, generic IRQ descriptors, and machine vectors that route device interrupts to `srm_device_interrupt()`.

**Risks:** Vector-to-IRQ arithmetic assumes SRM vector layout. PAL SMP safety is uncertain, hence the lock. Incorrect `max` or `ignore_mask` from platform code can expose firmware-reserved vectors. Firmware failures may not be visible to Linux.

**Test signals:** On SRM-managed systems, test enable/disable under SMP, device IRQ delivery from vectors, ignored-vector behavior, and level IRQ handling. Verify no concurrent PAL cserve calls occur under interrupt load.

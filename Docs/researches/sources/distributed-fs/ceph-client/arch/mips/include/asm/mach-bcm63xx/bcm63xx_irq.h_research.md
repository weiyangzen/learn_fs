# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_irq.h

**Purpose:** Defines BCM63xx base Linux IRQ numbers for internal and external interrupts.

**Important APIs/types/functions:** Exports `IRQ_INTERNAL_BASE` as 8, `IRQ_EXTERNAL_BASE` as 100, and external IRQ aliases `IRQ_EXT_0` through `IRQ_EXT_3`. It includes `bcm63xx_cpu.h`.

**Control flow:** `bcm63xx_cpu.h` per-CPU IRQ tables offset internal device IRQs from `IRQ_INTERNAL_BASE`, while board/interrupt code uses `IRQ_EXT_*` for external lines.

**State and persistence behavior:** No state. Numeric values form a compile-time IRQ numbering contract.

**Dependencies and integration points:** Integrated by CPU IRQ tables, interrupt controller setup, GPIO/external IRQ handling, and platform-device resources.

**Risks:** Header include ordering is delicate because `bcm63xx_cpu.h` also uses `IRQ_INTERNAL_BASE` in per-CPU constants. Changing bases breaks all fixed IRQ resource mappings.

**Test signals:** Build BCM63xx IRQ users, boot and inspect `/proc/interrupts`, trigger internal devices and external IRQ lines, and verify no overlap between internal/high/external ranges.

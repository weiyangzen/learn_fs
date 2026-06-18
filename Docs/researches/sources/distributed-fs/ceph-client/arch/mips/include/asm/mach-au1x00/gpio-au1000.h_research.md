# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/gpio-au1000.h

**Purpose:** Provides legacy Au1000/Au1100/Au1500/Au1550/Au1200 GPIO helpers and GPIO-to-IRQ mappings for GPIO1 and GPIO2 blocks.

**Important APIs/types/functions:** Defines GPIO number spaces `ALCHEMY_GPIO1_BASE` and `ALCHEMY_GPIO2_BASE`, register offsets for SYS GPIO1 and GPIO2 block, per-SoC `gpio*_to_irq()` and `irq_to_gpio()` helpers, GPIO value/direction/validity helpers, `alchemy_gpio1_input_enable()`, GPIO2 interrupt enable/disable helpers, GPIO2 block enable/disable, and wrapper APIs `alchemy_gpio_direction_input/output()`, `alchemy_gpio_get/set_value()`, `alchemy_gpio_is_valid()`, `alchemy_gpio_to_irq()`, and `alchemy_irq_to_gpio()`.

**Control flow:** Callers select GPIO1 or GPIO2 based on GPIO number, then helpers branch on `alchemy_get_cputype()` to apply SoC-specific IRQ routing. Direction/value helpers write raw SYS or GPIO2 registers, and shared-interrupt helpers gate per-pin contribution for grouped GPIO2 IRQs.

**State and persistence behavior:** No private state. The helpers mutate GPIO output, direction, input-enable, interrupt-enable, and block-enable hardware registers. They use local IRQ save/restore around GPIO2 direction and interrupt-enable register read-modify-write sequences.

**Dependencies and integration points:** Depends on `au1000.h`, KSEG1 raw MMIO, local IRQ control, and Linux error code `-ENXIO` through include context. Integrated by early board code and gpiolib registration paths.

**Risks:** GPIO/IRQ mappings differ sharply by SoC, and some GPIO2 interrupt lines are shared. Wrapper helpers do not validate every range before MMIO. GPIO1 input enable has different semantics across chip generations. Read-modify-write protection is local CPU only.

**Test signals:** Test direction/value operations before and after gpiolib registration, per-SoC GPIO-to-IRQ and IRQ-to-GPIO mapping, shared GPIO2 interrupt enable bits, GPIO2 block power enable/disable, and input behavior after `alchemy_gpio1_input_enable()`.

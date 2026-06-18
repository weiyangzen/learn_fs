# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pfunc_base.c

Purpose: installs base platform-function handlers for mac-io GPIOs, mac-io MMIO registers, UniNorth MMIO registers, and selected UniNorth hardware-clock nodes. These handlers execute firmware-provided `platform-do-*` bytecode through the PMF core.

Important APIs/types/functions: exported lifecycle functions are `pmac_pfunc_base_install`, `pmac_pfunc_base_suspend`, and `pmac_pfunc_base_resume`. Handler tables include `macio_gpio_handlers`, `macio_mmio_handlers`, and `unin_mmio_handlers`. Key callbacks include `macio_do_gpio_irq_enable`, `macio_do_gpio_irq_disable`, `macio_do_gpio_write`, `macio_do_gpio_read`, `macio_do_write_reg32`, `macio_do_read_reg32`, `macio_do_write_reg8`, `macio_do_read_reg8`, masked/shifted read/write helpers, and `unin_do_write_reg32`.

Control flow: `pmac_pfunc_base_install` runs once for PowerMac, iterates all probed `macio_chips`, registers MMIO handlers on each mac-io node, registers GPIO handlers for every child under a `gpio` node, runs GPIO on-init functions, and registers UniNorth handlers when mapped. GPIO interrupt enable maps the node IRQ and calls `request_irq`; the IRQ handler calls `pmf_do_irq`. Register handlers apply masks under `feature_lock` and use `MACIO_IN/OUT` or `UN_IN/OUT` accessors. Suspend and resume run PMF functions with `PMF_FLAGS_ON_SLEEP` and `PMF_FLAGS_ON_WAKE` in ordered mac-io/UniNorth sequences.

State and persistence: this file adds no durable storage. PMF registration creates global PMF devices/functions in `pfunc_core.c`; `unin_hwclock` stores the optional direct-mapped hardware-clock node for later PM callbacks. Hardware register and GPIO values are the persisted platform state across calls.

Dependencies/integration: depends on `macio_chips` and `uninorth_node` from `feature.c`, `feature_lock`, PMF core registration/execution APIs, OF node walking, IRQ mapping, and mac-io/UniNorth register macros.

Risks: GPIO offsets from old-style device trees are adjusted by a hard-coded `0x50` rule. Handler driver data stores MMIO addresses as raw pointers or `macio_chip` pointers, so incorrect PMF node registration can write arbitrary platform registers. GPIO IRQ enable does not store the mapped IRQ in the function, so disable remaps it later. The file comments state that GPIO at-sleep/at-wake functions are not implemented here.

Test signals: verify PMF registration for mac-io root, GPIO children, UniNorth, and `hw-clock`; run on-init GPIO and MMIO functions; test masked writes and shifted read/write return paths; register/unregister GPIO IRQ clients and trigger `pmf_do_irq`; suspend/resume sequencing for mac-io and UniNorth functions; malformed GPIO `reg` properties and old-style offset handling.

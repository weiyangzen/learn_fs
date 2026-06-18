## sources/distributed-fs/ceph-client/drivers/mfd/wm8994-irq.c

Purpose: this file implements the WM8994-family interrupt controller glue used by the MFD core. It maps codec status bits and GPIO interrupt bits into Linux nested IRQs through regmap-irq and provides an extra GPIO-backed wrapper for platforms whose top-level interrupt is edge triggered.

Important APIs, types, and functions: `wm8994_irqs[]` maps `WM8994_IRQ_*` logical IRQ numbers to masks and register offsets. `wm8994_irq_chip` describes two status/mask/ack registers starting at `WM8994_INTERRUPT_STATUS_1`. `wm8994_irq_init()` and `wm8994_irq_exit()` are exported. Edge-trigger support uses `wm8994_edge_irq_chip`, `wm8994_edge_irq()`, `wm8994_edge_irq_map()`, and a one-entry irqdomain.

Control flow: `wm8994_irq_init()` returns early if no parent IRQ is available. Otherwise it selects platform IRQ flags or defaults to high-level oneshot. For rising/falling edge flags, it requests the platform IRQ GPIO, creates a linear irqdomain with one virtual IRQ, adds the regmap IRQ chip behind that nested virtual IRQ, then requests a threaded top-level IRQ that loops while the GPIO line is asserted and dispatches the nested IRQ. For level-triggered cases it adds the regmap IRQ chip directly on the parent IRQ. Finally it unmasks the top-level codec interrupt by writing zero to `WM8994_INTERRUPT_CONTROL`.

State and persistence: persistent state is stored in `wm8994->irq`, `wm8994->irq_base`, `wm8994->irq_data`, and, for edge mode, `wm8994->edge_irq`. Mask/cache state is maintained by regmap-irq over the hardware interrupt mask registers. `wm8994_irq_exit()` deletes the regmap IRQ chip.

Dependencies and integration points: depends on gpiolib, irqdomain, regmap-irq, nested threaded IRQ handling, and WM8994 register definitions. Codec and GPIO child MFD cells consume the logical IRQ resources published by the parent.

Risks and test signals: edge-mode setup assumes `pdata->irq_gpio` is valid and can be converted to the parent IRQ; irqdomain allocation failure is not checked before mapping. A table entry for `WM8994_IRQ_GPIO(9)` uses `WM8994_GP8_EINT`, which is suspicious because GPIO 9 would normally be expected to use a GP9 mask if one exists. Test signals include parent IRQ registration, child IRQ mappings, mask/unmask behavior through regmap, interrupt ack by status-register write, and edge-mode repeated dispatch while the GPIO line remains asserted.

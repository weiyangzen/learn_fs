# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mt7621.c

Purpose: supports the MediaTek/Ralink MT7621 GPIO controller as three 32-line banks, each exposed as a separate gpiochip with shared parent IRQ support.

Important APIs/types/functions: `struct mtk` stores the device, MMIO base, parent IRQ, and three `struct mtk_gc` bank structures. `struct mtk_gc` wraps `gpio_generic_chip`, per-bank IRQ chip, bank id, and software trigger masks for rising/falling/high/low. Helpers `mtk_gpio_r32()` and `mtk_gpio_w32()` add bank stride to register offsets. GPIO setup uses `gpio_generic_chip_init()`. IRQ callbacks handle status scanning, mask/unmask, type, and OF translation.

Control flow: platform probe maps resource 0, gets the parent IRQ, stores drvdata, then probes banks 0-2. Each bank initializes a generic chip over DATA/DSET/DCLR/CTRL registers with `GPIO_GENERIC_NO_SET_ON_INPUT`, sets OF two-cell translation, labels and offsets the bank, requests the shared parent IRQ with bank-specific data, configures an internal IRQ chip, registers the gpiochip, and sets polarity low. The IRQ handler reads bank status, dispatches each pending bit through the bank's IRQ domain, then clears that bit.

State and persistence behavior: hardware registers hold direction/data/polarity/status. Desired trigger modes are cached in `rising`, `falling`, `hlevel`, and `llevel`; unmask writes those cached masks to hardware enable registers. There is no suspend/resume save path.

Dependencies and integration points: depends on OF compatible `mediatek,mt7621-gpio`, shared parent IRQ, generic MMIO GPIO helper, and OF GPIO translation where global GPIO numbers are mapped to bank-local offsets.

Risks: `mediatek_gpio_irq_type()` does not reject unsupported trigger types; if no case matches, it clears all cached trigger bits and returns success. Shared parent IRQ is requested once per bank with `IRQF_SHARED`, so status isolation by bank register offset must be correct. No PM restore may lose trigger caches versus hardware after suspend.

Test signals: three bank registration, OF xlate rejecting wrong-bank GPIO specifiers, generic get/set/direction behavior, IRQ type cache updates, mask/unmask programming of edge/level registers, status dispatch and clearing per bank, and invalid trigger handling.

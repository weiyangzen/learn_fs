# sources/distributed-fs/ceph-client/drivers/mfd/motorola-cpcap.c

Purpose: SPI MFD core for Motorola CPCAP PMICs. It initializes a 16-bit little-endian regmap, validates vendor/revision, builds three regmap IRQ chips, exports interrupt-sense helper functionality, and registers numerous CPCAP child devices.

Important APIs, types, and functions: `struct cpcap_ddata` stores SPI, regmap, IRQ arrays, and regmap configuration. `cpcap_sense_virq()` is exported so children can sample current interrupt sense state. `cpcap_check_revision()` reads vendor and revision through public CPCAP helpers. `cpcap_init_irq()` allocates regmap IRQ descriptors and initializes two macro IRQ chips plus one 64-IRQ child chip. `cpcap_probe()` sets SPI mode, initializes regmap, validates revision, initializes IRQs, adjusts DMA masks, and calls `devm_mfd_add_devices()`.

Control flow: probe configures SPI for 16-bit words and chip-select-high, sets up regmap, rejects unsupported old revisions, creates IRQ chips on the same parent IRQ, enables wake on the parent IRQ, then registers child cells for ADC, battery, charger, regulator, RTC, pwrbutton, USB PHY, LEDs, and codec. Suspend disables the parent IRQ; resume re-enables it.

State and persistence: all runtime state is devm-managed in `cpcap_ddata`. IRQ chip state is owned by regmap-irq. Hardware interrupt masks/acks persist in CPCAP registers. The parent IRQ is configured as a wake source.

Dependencies and integration points: depends on SPI core, regmap, regmap-irq, public `<linux/mfd/motorola-cpcap.h>`, and OF compatibles `motorola,cpcap` and `st,6556002`. Child matching uses many `of_compatible` strings.

Risks: `enable_irq_wake()` return value is ignored and there is no matching disable in remove. All three regmap IRQ chips share one physical IRQ with `IRQF_SHARED`, which requires careful child status handling. Older revisions are rejected entirely. Test signals include revision detection, three IRQ-chip mapping ranges, exported `cpcap_sense_virq()`, wake IRQ behavior, child OF node matching, and SPI endian/register-stride correctness.

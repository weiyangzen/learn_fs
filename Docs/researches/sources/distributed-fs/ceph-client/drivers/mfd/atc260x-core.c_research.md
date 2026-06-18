<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atc260x-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atc260x-core.c

Purpose: implements interface-independent core support for Actions ATC2603C and ATC2609A PMICs. It selects variant-specific regmap/IRQ/child-cell configuration, initializes interrupt hardware, detects chip revision, registers a regmap IRQ chip, and creates regulator, power-controller, and onkey children.

Important APIs and functions: exported APIs are `atc260x_match_device` and `atc260x_device_probe`. Helpers include custom `regmap_lock_mutex`/`regmap_unlock_mutex`, `atc260x_cmu_reset`, and `atc260x_dev_init`. Variant tables define 16-bit register maps, one-register IRQ chips, onkey IRQ resources, MFD cells, and reset/pad register addresses.

Control flow: bus drivers allocate `struct atc260x`, set `dev` and `irq`, call `atc260x_match_device` to fill regmap config and variant fields, initialize bus regmap, then call `atc260x_device_probe`. The probe path requires an IRQ, resets the interrupt block through CMU registers, masks all interrupts, enables the EXTIRQ pad, reads and validates the chip revision, derives an alphabetic revision from the one-hot revision value, registers the regmap IRQ chip, and adds child devices with the IRQ domain.

State and persistence: `struct atc260x` stores type, revision, regmap, IRQ, regmap IRQ data, cell table, type name, revision register, init register pointers, and a custom regmap mutex. The PMIC hardware retains regulator/power/interrupt state; this core does not use regcache.

Dependencies and integration points: depends on OF match data, regmap, regmap IRQ, MFD core, Linux interrupt support, and public ATC260x core macros/types. The custom regmap lock is designed to improve late shutdown/poweroff behavior on slow buses when interrupts are disabled.

Risks: `regmap_lock_mutex` uses `mutex_trylock` in late atomic-ish paths but `regmap_unlock_mutex` always unlocks, so correctness relies on trylock succeeding when invoked. No-IRQ configurations fail probe. Revision decoding assumes `chip_rev + 1` has a valid set bit and rejects values above 31. Manual `regmap_del_irq_chip` on `devm_mfd_add_devices` failure is unusual because the IRQ chip was devm-registered.

Test signals: probe both ATC2603C and ATC2609A OF compatibles, verify interrupt reset/mask/pad writes, chip revision detection, onkey IRQ delivery, child regulator/power-controller operation, no-IRQ failure behavior, and shutdown/poweroff code paths that exercise the custom regmap lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atc260x-core.c -->

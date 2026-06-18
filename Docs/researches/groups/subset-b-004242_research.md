# subset-b-004242 research

This grouped report covers MFD, PMIC, embedded-controller, USB bridge, and PRCMU files under `sources/distributed-fs/ceph-client/drivers/mfd`. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9052-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9052-core.c

## Purpose
`da9052-core.c` is the common MFD core for Dialog DA9052/DA9053 PMICs. It defines the regmap access policy, ADC helpers, fault-log handling, and the child device set shared by the I2C and SPI bus front-ends.

## Important APIs, Types, and Functions
The exported `da9052_regmap_config` constrains readable, writeable, and volatile registers with `da9052_reg_readable()`, `da9052_reg_writeable()`, and `da9052_reg_volatile()`. Exported helpers `da9052_adc_manual_read()` and `da9052_adc_read_temp()` provide manual ADC conversions and battery-temperature lookup. `da9052_device_init()` and `da9052_device_exit()` are called by bus drivers. `da9052_clear_fault_log()` records and clears reset/fault causes. `da9052_subdev_info` and `da9052_tsi_subdev_info` enumerate regulator, onkey, RTC, GPIO, hwmon, LED, battery, watchdog, and optional touchscreen children.

## Control Flow
The bus driver allocates `struct da9052`, initializes the regmap, and calls `da9052_device_init()`. Core init creates the ADC mutex/completion, clears the fault log, calls optional platform init, sets the chip id, initializes the regmap IRQ chip through `da9052_irq_init()`, registers common MFD children, and conditionally registers the TSI child unless `dlg,tsi-as-adc` is present. Manual ADC reads serialize on `auxadc_lock`, program `DA9052_ADC_MAN_REG`, wait up to 500 ms for the ADC completion, and combine high/low result registers.

## State and Persistence
Runtime state lives in `struct da9052`: regmap, chip id, IRQ data, fault log, ADC mutex, and ADC completion. Hardware state is the PMIC register file, including volatile status/event/ADC/RTC fields. The driver does not persist state across reboot; it only captures the current fault log in memory before clearing it in hardware.

## Dependencies and Integration Points
The file depends on Linux regmap, MFD core, property APIs, DA9052 register definitions, and `da9052_irq_init()` from the IRQ companion file. Child drivers consume named MFD devices and internal IRQ resources. `device_property_read_bool()` allows device tree or ACPI-style firmware to alter TSI registration.

## Risks and Edge Cases
`da9052_device_init()` clears the fault log before `chip_id` is assigned, while bus-specific I/O errata handling may depend on `chip_id`; platforms relying on the I2C parking fix during the earliest reads need careful validation. ADC reads fail on invalid channel, IRQ timeout, or register I/O error. The TBAT lookup assumes an 8-bit result and treats zero or negative register returns as errors. If TSI pins are physically used as ADC inputs but `dlg,tsi-as-adc` is omitted, an unwanted touchscreen child is created.

## Test Signals
Useful signals include regmap access-table acceptance of expected PMIC registers, fault-log read/clear logs, successful child registration, ADC conversion interrupt completion, timeout behavior with the ADC IRQ masked, TBAT lookup values, and `dlg,tsi-as-adc` toggling TSI child creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9052-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9052-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9052-i2c.c

## Purpose
`da9052-i2c.c` is the I2C transport driver for DA9052 and DA9053 PMIC variants. It binds I2C/OF IDs, creates the shared core object, applies I2C errata workarounds, and hands control to the common DA9052 MFD core.

## Important APIs, Types, and Functions
`i2c_safe_reg()` identifies registers safe for dummy reads. `da9052_i2c_fix()` performs the post-access parking read required for DA9052 and DA9053 AA/BA/BB. `da9052_i2c_disable_multiwrite()` sets `DA9052_CONTROL_B_WRITEMODE` to avoid errata item 24. `da9052_i2c_probe()` and `da9052_i2c_remove()` are the driver lifecycle callbacks; `da9052_i2c_id` and `dialog_dt_ids` map names and compatibles to chip IDs.

## Control Flow
Probe allocates `struct da9052`, stores the device and chip IRQ, assigns `fix_io`, creates a regmap with `da9052_regmap_config`, disables multiwrite mode, resolves an I2C or OF match ID, and calls `da9052_device_init()`. Remove calls `da9052_device_exit()`. The driver registers at `subsys_initcall()` time so PMIC services are available early to other subsystems.

## State and Persistence
The file stores only per-client state through I2C client data. The persistent hardware effect is disabling multiwrite mode in `CONTROL_B`; all other state is volatile PMIC/register state managed by the core.

## Dependencies and Integration Points
It depends on I2C, OF matching, regmap-I2C, DA9052 core helpers, and the core register definitions. The core later integrates child devices and regmap IRQs.

## Risks and Edge Cases
The I2C parking workaround depends on `chip_id`; this file sets `chip_id` through the `da9052_device_init()` argument after some early register accesses, so early accesses are not protected by variant-aware parking. Missing ID data returns `-ENODEV`. Disabling multiwrite is mandatory for the erratum; failure aborts probe.

## Test Signals
Probe with each supported compatible, verify `CONTROL_B_WRITEMODE` is set, observe dummy parking reads after non-safe register access on affected variants, confirm no parking on DA9053_BC, and verify remove unregisters MFD children and IRQ data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9052-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9052-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9052-irq.c

## Purpose
`da9052-irq.c` exposes the DA9052 PMIC event registers as Linux virtual IRQs using regmap-irq and provides convenience wrappers for DA9052 child drivers.

## Important APIs, Types, and Functions
`da9052_irqs[]` maps 32 PMIC events across `EVENT_A` through `EVENT_D`. `da9052_regmap_irq_chip` defines status, mask, and ack bases. Exported wrappers `da9052_enable_irq()`, `da9052_disable_irq()`, `da9052_disable_irq_nosync()`, `da9052_request_irq()`, and `da9052_free_irq()` translate PMIC IRQ IDs through `regmap_irq_get_virq()`. `da9052_auxadc_irq()` completes the core ADC conversion. `da9052_irq_init()` and `da9052_irq_exit()` install and remove the IRQ chip.

## Control Flow
Initialization calls `regmap_add_irq_chip()` on the parent PMIC IRQ with low-triggered oneshot handling, enables wake on the parent IRQ, and registers a threaded ADC end-of-measurement handler. Child drivers call the exported wrappers with DA9052 logical IRQ IDs; the wrappers map to virtual IRQs and call generic IRQ APIs. Exit frees the ADC IRQ and deletes the regmap IRQ chip.

## State and Persistence
`da9052->irq_data` owns the regmap IRQ domain state. Event status and mask bits persist only in the PMIC register file. The ADC completion state is stored in the core object and signaled by the ADC event handler.

## Dependencies and Integration Points
The file depends on regmap-irq, Linux IRQ threading, and DA9052 register/IRQ enums. It integrates directly with `da9052_adc_manual_read()` and with child drivers that request PMIC-local interrupt lines.

## Risks and Edge Cases
All PMIC child IRQs depend on a valid parent `chip_irq`; absent or incorrectly triggered hardware IRQs will break ADC reads and child events. `enable_irq_wake()` is not unwound explicitly in exit. The helper uses low-triggered oneshot flags for child requests, so mismatched electrical configuration can cause repeated interrupts.

## Test Signals
Check creation of 32 virtual IRQs, status/mask/ack writes around event delivery, ADC completion behavior, child request/free paths, parent wake capability, and cleanup after failed ADC IRQ registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9052-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9052-spi.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9052-spi.c

## Purpose
`da9052-spi.c` is the SPI transport front-end for DA9052/DA9053 PMICs. It configures SPI framing, adapts the shared DA9052 regmap configuration to the SPI protocol, and invokes the MFD core.

## Important APIs, Types, and Functions
`da9052_spi_probe()` allocates the core object, configures SPI mode and word size, builds a local `regmap_config` with SPI-specific read flag, register, pad, and value widths, and calls `da9052_device_init()`. `da9052_spi_remove()` calls `da9052_device_exit()`. `da9052_spi_id` maps SPI device names to DA9052 variant IDs.

## Control Flow
Probe sets `SPI_MODE_0` and 8-bit words, performs `spi_setup()`, creates a single-read/single-write regmap, and initializes the common PMIC core with the matched variant. Remove reverses by delegating to the core. Registration also uses `subsys_initcall()` for early PMIC availability.

## State and Persistence
Per-device state is stored in `struct da9052` attached to the SPI device. No filesystem persistence exists. SPI mode and PMIC register state are the only hardware-facing state.

## Dependencies and Integration Points
It depends on SPI, regmap-SPI, and `da9052_device_init()`. The bus file shares child registration, ADC, and IRQ behavior with the I2C front-end through the core.

## Risks and Edge Cases
`spi_setup()` return value is ignored; a failed SPI mode setup could lead to later regmap failures or bad transfers. There is no OF match table in this file, so matching is via SPI IDs. The SPI config forces single reads/writes, which is conservative but can affect throughput.

## Test Signals
Validate SPI mode/word-size setup, regmap transfer framing with 7-bit register plus pad/read flag, variant ID propagation, MFD child creation, and failure behavior when regmap initialization fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9052-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9055-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9055-core.c

## Purpose
`da9055-core.c` is the common MFD core for the Dialog DA9055 PMIC. It defines regmap access policy, the PMIC interrupt chip, child MFD devices, and the init/exit routines used by the I2C transport.

## Important APIs, Types, and Functions
`da9055_register_readable()`, `da9055_register_writeable()`, and `da9055_register_volatile()` define the exported `da9055_regmap_config`. `da9055_irqs[]` maps onkey, alarm, tick, hwmon, and regulator current-limit events. `da9055_regmap_irq_chip` exposes the three event/mask registers. `da9055_devs[]` lists GPIO, regulators, onkey, RTC, hwmon, and watchdog children. `da9055_device_init()` and `da9055_device_exit()` are exported to the bus driver.

## Control Flow
Initialization runs optional platform init, selects either a platform-provided IRQ base or dynamic base, clears all event registers with a three-byte group write, installs the regmap IRQ chip on `chip_irq`, records the assigned IRQ base, and registers all child devices with that IRQ base. Failure after IRQ setup removes the regmap IRQ chip. Exit deletes the IRQ chip and removes children.

## State and Persistence
State is held in `struct da9055`: regmap, device pointer, chip IRQ, IRQ base, and regmap IRQ data. Hardware state consists of PMIC event/mask/control/regulator/RTC registers. There is no persistence beyond PMIC hardware retention.

## Dependencies and Integration Points
This core depends on regmap, regmap-irq, MFD core, DA9055 register definitions, and optional platform data. Child drivers receive compatible strings and named IRQ resources.

## Risks and Edge Cases
`DA9055_IRQ_ADC_MASK` and `DA9055_IRQ_BUCK_ILIM_MASK` both use bit `0x08` but in different event-register offsets; offset correctness is essential. `da9055_device_exit()` deletes the IRQ chip before removing children, which can matter if child remove paths expect live IRQ mappings. Event clearing at init can discard events that occurred before Linux handled them.

## Test Signals
Check regmap access filters, event clear writes to A/B/C, IRQ base assignment, child resources for RTC/hwmon/regulator/onkey, dynamic and fixed IRQ base operation, and cleanup after `mfd_add_devices()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9055-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9055-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9055-i2c.c

## Purpose
`da9055-i2c.c` is the I2C transport driver for the DA9055 PMIC portion. It creates the regmap and delegates MFD setup to `da9055-core.c`.

## Important APIs, Types, and Functions
`da9055_i2c_probe()` allocates `struct da9055`, creates a regmap with `da9055_regmap_config`, records device and IRQ information, and calls `da9055_device_init()`. `da9055_i2c_remove()` calls `da9055_device_exit()`. The ID table intentionally uses `da9055-pmic` to distinguish the PMIC I2C function from the codec function.

## Control Flow
On probe, the driver initializes regmap-I2C first, then stores client data and invokes the core. On remove, it retrieves client data and exits the core. Driver registration uses `subsys_initcall()` for early PMIC registration.

## State and Persistence
The only local state is the client-attached `struct da9055`. Hardware state is managed through regmap and the core; nothing is persisted by this file.

## Dependencies and Integration Points
It depends on I2C, OF matching for `dlg,da9055-pmic`, regmap-I2C, and DA9055 core APIs. The naming convention integrates with systems where DA9055 PMIC and codec appear as separate I2C clients.

## Risks and Edge Cases
Changing the device ID string can break systems that instantiate PMIC and codec separately. Probe aborts if regmap initialization fails. The remove path assumes core init succeeded enough for `da9055_device_exit()` to be safe.

## Test Signals
Probe via I2C ID and OF compatible, confirm separate PMIC/CODEC enumeration, validate child device creation, and check remove unregisters children and IRQ chip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9055-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9062-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9062-core.c

## Purpose
`da9062-core.c` is a combined I2C, MFD, regmap, and IRQ driver for Dialog DA9061 and DA9062 PMICs. It selects chip-specific access tables and child devices, validates hardware identity, configures IRQ polarity, and registers the PMIC children.

## Important APIs, Types, and Functions
`da9061_irqs[]` and `da9062_irqs[]` describe event bits for each chip family. `da9061_irq_chip` and `da9062_irq_chip` expose three event/mask registers. `da9061_devs_irq/noirq` and `da9062_devs_irq/noirq` describe child devices with and without IRQ resources. `da9062_clear_fault_log()`, `da9062_get_device_type()`, and `da9062_configure_irq_type()` perform setup checks. The many `regmap_range` and `regmap_access_table` definitions encode DA9061/DA9062 readable, writeable, and volatile register windows.

## Control Flow
Probe allocates `struct da9062`, gets the chip type from OF/I2C match data, chooses the no-IRQ child list and regmap config, creates the I2C regmap, switches to I2C mode when full I2C functionality is available, clears the fault log, validates the device and variant ID, then conditionally reselects IRQ-capable child cells and the proper regmap IRQ chip if `i2c->irq` exists. IRQ setup programs `CONFIG_A` according to the parent IRQ trigger type, adds a shared oneshot regmap IRQ chip, and passes the assigned IRQ base to `mfd_add_devices()`.

## State and Persistence
`struct da9062` holds device, regmap, type, and regmap IRQ data. The driver updates persistent hardware registers such as `CONFIG_J` bus mode, `CONFIG_A` IRQ type, and clears fault-log/event registers. Regmap uses `REGCACHE_MAPLE`, but no explicit suspend persistence is implemented here.

## Dependencies and Integration Points
It depends on I2C, OF matching, regmap ranges, regmap-irq, MFD core, and DA9062 regulator/watchdog/thermal/RTC/onkey/GPIO children. Parent IRQ trigger type is read from the IRQ descriptor and mirrored into PMIC configuration.

## Risks and Edge Cases
`da9062_i2c_remove()` always calls `regmap_del_irq_chip(i2c->irq, chip->regmap_irq)` even though probe supports no-IRQ mode; a no-IRQ probed instance could expose an invalid cleanup path. Unsupported parent IRQ types abort probe. `da9062_get_device_type()` logs the variant but only rejects too-old MRC; it does not require the VRC to match the selected compatible. Event clearing can discard pre-boot events.

## Test Signals
Test DA9061 and DA9062 compatibles, no-IRQ and IRQ-equipped systems, low/high parent IRQ configuration, invalid edge IRQ rejection, register access-table coverage, child resources, fault-log clearing, and remove behavior in no-IRQ configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9062-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9063-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9063-core.c

## Purpose
`da9063-core.c` is the common MFD core for Dialog DA9063 and DA9063L PMICs. It clears fault logs, initializes the interrupt subsystem, and registers common and DA9063-only child devices.

## Important APIs, Types, and Functions
Resource arrays describe regulator, RTC, onkey, and hwmon IRQs. `da9063_common_devs[]` registers regulators, LEDs, watchdog, hwmon, onkey, and vibration children. `da9063_devs[]` registers the RTC child only for full DA9063, not DA9063L. `da9063_clear_fault_log()` reports and clears PMIC fault bits. `da9063_device_init()` is the core init entry called by the I2C driver.

## Control Flow
`da9063_device_init()` clears the fault log, initializes flags and IRQ fields, calls `da9063_irq_init()`, records the regmap IRQ base, registers common children via `devm_mfd_add_devices()`, and conditionally registers DA9063-only RTC support when `da9063->type == PMIC_TYPE_DA9063`.

## State and Persistence
State is stored in `struct da9063`: type, variant, flags, chip IRQ, IRQ base, regmap, and regmap IRQ data. Hardware fault-log state is cleared by writing back the read fault bits. Child devices are devm-managed.

## Dependencies and Integration Points
The file depends on regmap, MFD core, DA9063 register definitions, and `da9063_irq_init()` from the IRQ file. Child drivers consume DA9063 driver-name constants and named IRQ resources.

## Risks and Edge Cases
Fault-log clearing writes the read value even when zero, so bus errors must be distinguished from harmless empty logs. The core requires IRQ initialization to succeed; platforms without a configured PMIC IRQ cannot register children. The file includes unused proc/kthread/uaccess headers, suggesting historical baggage but no runtime effect.

## Test Signals
Verify DA9063 versus DA9063L child differences, fault-log bit reporting and clearing, regmap IRQ base propagation, child IRQ resource mapping, and probe failure when the parent IRQ is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9063-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9063-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9063-i2c.c

## Purpose
`da9063-i2c.c` is the I2C bus driver and variant-specific regmap selector for DA9063 and DA9063L PMICs. It performs raw paged reads before regmap setup to identify chip variant and then installs the correct access tables.

## Important APIs, Types, and Functions
`da9063_i2c_blockreg_read()` performs manual page selection and block reads using I2C transfers. `da9063_get_device_type()` reads device and variant IDs. Multiple `regmap_range` and `regmap_access_table` sets cover DA9063 AD, BB/CA, DA/EA and DA9063L BB/CA, DA/EA register layouts. `da9063_range_cfg` models 256-byte pages selected through `DA9063_REG_PAGE_CON`. `da9063_i2c_probe()` selects tables, creates the regmap, optionally switches bus mode, reserves the secondary I2C address, and calls `da9063_device_init()`.

## Control Flow
Probe allocates the core object, records the matched PMIC type, raw-reads chip IDs before regmap exists, chooses the access table based on type and `variant_code`, initializes the I2C regmap, clears two-wire timeout mode when full I2C is supported, creates a dummy client at `addr + 1` to reserve the PMIC's second address, and delegates to the core.

## State and Persistence
The driver stores type and variant in `struct da9063`. It mutates the file-scope `da9063_regmap_config` by assigning access-table pointers before `devm_regmap_init_i2c()`. Hardware state changes include page select accesses, `CONFIG_J` bus-mode update, and address reservation through a dummy I2C device.

## Dependencies and Integration Points
It depends on I2C transfer APIs, regmap range windows, OF/I2C matching, and `da9063_device_init()`. It integrates with the I2C core by claiming the secondary address to prevent userspace or another driver from binding it.

## Risks and Edge Cases
`da9063_regmap_config` is a mutable static shared by all instances, so multiple devices with different variants could race or inherit the wrong access tables. `devm_i2c_new_dummy_device()` return value is ignored, so secondary-address reservation failure does not fail probe. Raw page reads reject addresses above page 1. Probe uses `i2c_client_get_device_id()` for type data, which can be fragile for OF-only binding if no ID is associated.

## Test Signals
Test each supported variant table, invalid device ID rejection, unsupported variant rejection, page-switch I2C transfer counts, secondary address reservation, I2C mode bit clearing, and multi-instance behavior if hardware can expose more than one PMIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9063-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9063-irq.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9063-irq.c

## Purpose
`da9063-irq.c` maps DA9063 and DA9063L PMIC event registers into regmap IRQ domains.

## Important APIs, Types, and Functions
`da9063_irqs[]` maps full DA9063 events across EVENT_A through EVENT_D, including RTC alarm/tick. `da9063l_irqs[]` omits DA9063-only alarm/tick support while keeping common onkey, ADC, wake, thermal, regulator, DVC, warning, and GPIO events. `da9063_irq_chip` and `da9063l_irq_chip` define four status/mask/ack registers with `init_ack_masked = true`. `da9063_irq_init()` selects the correct chip and adds it with `devm_regmap_add_irq_chip()`.

## Control Flow
The core calls `da9063_irq_init()` after the regmap exists and before children are added. The function rejects missing parent IRQs, chooses DA9063 or DA9063L mapping by type, and installs a low-triggered shared oneshot regmap IRQ chip using the current IRQ base.

## State and Persistence
Regmap-irq owns virtual IRQ mappings and mask/cache state in `da9063->regmap_irq`. PMIC event and mask registers are volatile hardware state. `init_ack_masked` causes masked pending events to be acknowledged during initialization.

## Dependencies and Integration Points
The file depends on regmap-irq, MFD core, DA9063 core/type definitions, and Linux IRQ flags. Child devices registered by the core receive resources that refer to these logical IRQ IDs.

## Risks and Edge Cases
The function hard-fails when no parent IRQ is configured, so even non-interrupt child functionality cannot register through this core. Shared low-trigger assumptions must match board wiring. DA9063L lacks alarm/tick entries; child resources must not request those on DA9063L.

## Test Signals
Check full versus L IRQ map sizes, parent IRQ absence failure, masked-pending ACK at init, GPIO event delivery across EVENT_C/D, and named resource mapping for onkey/hwmon/RTC/regulator children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9063-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9150-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/da9150-core.c

## Purpose
`da9150-core.c` is the MFD core and I2C driver for the Dialog DA9150 charger/fuel-gauge/GPADC device. It provides exported register/QIF helpers, regmap IRQ support, child device registration, and shutdown behavior.

## Important APIs, Types, and Functions
Raw QIF helpers `da9150_i2c_read_device()` and `da9150_i2c_write_device()` implement STOP/START read semantics. Exported APIs include `da9150_read_qif()`, `da9150_write_qif()`, `da9150_reg_read()`, `da9150_reg_write()`, `da9150_set_bits()`, `da9150_bulk_read()`, and `da9150_bulk_write()`. `da9150_volatile_reg()` and `da9150_regmap_config` define paged regmap behavior. `da9150_irqs[]` and `da9150_regmap_irq_chip` expose EVENT_E through EVENT_H. `da9150_devs[]` registers GPADC, charger, and fuel-gauge children.

## Control Flow
Probe allocates `struct da9150`, initializes the paged I2C regmap, reads the secondary QIF base address from `CORE2WIRE_CTRL_A`, creates a dummy I2C QIF client, applies optional platform fuel-gauge data, installs the regmap IRQ chip, enables wake on the parent IRQ, and adds child devices. Remove deletes the IRQ chip, removes children, and unregisters the QIF client. Shutdown enables PM wake and sets the device disabled bit.

## State and Persistence
State includes the primary I2C client, secondary QIF client, regmap, IRQ base, and regmap IRQ data. Hardware state includes paged PMIC registers, QIF address routing, event/mask bits, wake configuration, and disabled mode set during shutdown.

## Dependencies and Integration Points
The driver depends on I2C, regmap, regmap-irq, MFD core, DA9150 register definitions, optional platform data, and child drivers for GPADC, charger, and fuel gauge. QIF helpers are exported for child use.

## Risks and Edge Cases
Raw QIF write allocates a temporary buffer for each access and can fail under memory pressure. `da9150_reg_read()` returns `u8`, so callers cannot distinguish a read error from an actual register value without logs. `enable_irq_wake()` is not explicitly disabled. Shutdown deliberately changes power state, so tests must avoid triggering it unexpectedly.

## Test Signals
Verify QIF dummy address calculation, STOP/START raw read behavior, paged regmap access, regmap IRQ events for charger/GPADC/fuel gauge, platform fuel-gauge data propagation, wake enablement, and shutdown writes to `CONFIG_D` and `CONTROL_C`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/da9150-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/db8500-prcmu-regs.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/db8500-prcmu-regs.h

## Purpose
`db8500-prcmu-regs.h` defines the DB8500 PRCMU register offsets and bit fields used by the PRCMU implementation. It is a hardware contract header for clock, PLL, mailbox, reset, clamp, semaphore, timer, GPIO, and power-management registers.

## Important APIs, Types, and Functions
The header provides the `BITS(_start, _end)` mask helper and many `PRCM_*` macros. Key groups include clock-management offsets such as `PRCM_UARTCLK_MGT`, ARM PLL/divider registers, mailbox CPU set/clear/value registers, interrupt status/clear/mask registers, PLLSOC/PLLDSI frequency fields, DSI clock divider fields, clock output fields, ePOD/memory power registers, hardware semaphore `PRCM_SEM`, timer control `PRCM_TCR`, GPIO routing bits, and reset registers.

## Control Flow
There is no executable control flow. The implementation includes this header and combines offsets with the global `prcmu_base` pointer for MMIO reads and writes.

## State and Persistence
The macros describe volatile PRCMU MMIO state. Persistence depends entirely on SoC reset and power-domain behavior; this header stores no state.

## Dependencies and Integration Points
The header assumes Linux `BIT()` is available and that `prcmu_base` is visible in the including C file for address-valued macros. It is tightly coupled to `db8500-prcmu.c` rather than a standalone generic header.

## Risks and Edge Cases
Many macros expand to pointer expressions using `prcmu_base`, so they cannot be safely used before the base is mapped. `PRCM_APE_SOFTRST` is defined twice with the same value. Register fields are SoC-specific; reuse for DB8520/U8540-style variants must be checked against hardware documentation.

## Test Signals
Validation signals are compile success after inclusion, correct MMIO addresses in early boot traces, expected clock/PLL bit manipulation, mailbox interrupt clear behavior, and no use before `prcmu_base` initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/db8500-prcmu-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/db8500-prcmu.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/db8500-prcmu.c

## Purpose
`db8500-prcmu.c` is the central PRCMU firmware interface for ST-Ericsson DB8500/Ux500 platforms. It handles PRCMU MMIO, TCDM mailboxes, power-state transitions, wakeups, OPP changes, ePOD power domains, autonomous PM, clocks, PLLs, thermal/watchdog commands, ABB I2C proxying, modem wake/sleep/reset, PRCMU IRQ demultiplexing, firmware version discovery, regulator data, and MFD child registration.

## Important APIs, Types, and Functions
Low-level exports include `db8500_prcmu_read()`, `db8500_prcmu_write()`, `db8500_prcmu_write_masked()`, and `prcmu_get_fw_version()`. Power/OPP APIs include `prcmu_set_rc_a2p()`, `prcmu_get_rc_p2a()`, `prcmu_get_xp70_current_state()`, `db8500_prcmu_set_power_state()`, `db8500_prcmu_enable_wakeups()`, `db8500_prcmu_set_arm_opp()`, `db8500_prcmu_set_ape_opp()`, `db8500_prcmu_request_ape_opp_100_voltage()`, `db8500_prcmu_set_epod()`, and `prcmu_configure_auto_pm()`. Clock APIs include `db8500_prcmu_request_clock()`, `prcmu_clock_rate()`, `prcmu_round_clock_rate()`, and `prcmu_set_clock_rate()`. Firmware command APIs cover hotmon/temp sense, A9 watchdog, ABB reads/writes, AC wake/sleep, system reset, reset-code retrieval, and modem reset. `prcmu_irq_handler()`, mailbox readers, and `prcmu_irq_chip` implement IRQ demux. `db8500_prcmu_early_init()` maps PRCMU early and initializes synchronization; `db8500_prcmu_probe()` performs full platform registration.

## Control Flow
Early init finds the `stericsson,db8500-prcmu` node, maps PRCMU registers, reads firmware version from the second region, and initializes locks/completions/work. Platform probe remaps named PRCMU and TCDM resources with devm, clears pre-kernel mailbox interrupts, requests the PRCMU IRQ as threaded, creates the PRCMU irqdomain, configures ESRAM0 sleep retention, registers watchdog/cpuidle/regulator/thermal children, and registers the AB8500/AB8505 child found in the device tree. Most firmware requests wait for the target mailbox bit to become free, write request payloads into TCDM, set the CPU mailbox bit, and wait for a completion populated by the IRQ handler. Mailbox 0 wake events can return `IRQ_WAKE_THREAD`; the thread ACKs DBB wakeups with a follow-up mailbox message.

## State and Persistence
Global state includes `prcmu_base`, `tcdm_base`, firmware info, the PRCMU irqdomain, mailbox transfer structures with locks/completions/ack caches, wakeup/IRQ request masks, clock-management cached PLL switch bits, DSI divider selections, autonomous PM enabled state, and AC wake atomic state. Hardware state spans PRCMU registers and TCDM mailboxes. Reset reason is persisted only in PRCMU TCDM until overwritten or reset by firmware.

## Dependencies and Integration Points
The driver depends on OF resources/IRQs, Linux IRQ domains, threaded IRQs, MFD core, AB8500 MFD integration, regulator init data, Ux500 PRCMU public headers, and MMIO helpers. It is the backend for clock, cpufreq, regulator, thermal, watchdog, cpuidle, ABB, modem, and reset users on DB8500-family systems.

## Risks and Edge Cases
Many paths busy-wait on mailbox or hardware semaphore availability with `cpu_relax()` and no timeout, so firmware lockups can hang callers. Several APIs use `BUG_ON()` for invalid caller input, making misuse fatal. Early and probe-time mappings both assign global `prcmu_base`; ordering is critical. `db8500_irq_init()` return value is ignored in probe. `request_threaded_irq()` is not released on later MFD registration failures. AC wake/sleep and mailbox completions have long timeouts but limited recovery. `prcmu_irq_mask()` compares `d->irq` against a hardware IRQ index constant, which is suspicious because `d->irq` is a Linux virq while `d->hwirq` is the PRCMU index.

## Test Signals
Important signals include firmware version logging, mailbox IRQ completions for MB1/2/4/5, wakeup IRQ demux through the PRCMU domain, clock request/rate/round/set behavior for register clocks, DSI PLL lock failure paths, ARM/APE OPP transitions, ePOD timeout handling, ABB I2C proxy read/write status, AC wake/sleep completion, reset-code round trip, MFD child registration, and boot under each supported firmware project name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/db8500-prcmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/dln2.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/dln2.c

## Purpose
`dln2.c` is the USB MFD core for the Diolan DLN-2 adapter. It provides a request/response transport for child GPIO, I2C, SPI, and ADC drivers, demultiplexes asynchronous events, manages USB bulk URBs, and registers hotplug MFD children.

## Important APIs, Types, and Functions
`struct dln2_header` and `struct dln2_response` define the USB message protocol. `struct dln2_rx_context` and `struct dln2_mod_rx_slots` manage per-module response slots indexed by echo values. `struct dln2_dev` stores USB endpoints, URBs, slot pools, callback list, and disconnect state. Exported APIs are `dln2_transfer()`, `dln2_register_event_cb()`, and `dln2_unregister_event_cb()`. Key internals include `dln2_rx()`, `dln2_transfer_complete()`, `_dln2_transfer()`, `dln2_check_hw()`, `dln2_setup_rx_urbs()`, `dln2_stop()`, `dln2_probe()`, suspend, resume, and disconnect.

## Control Flow
Probe binds only interface 0, locates bulk endpoints, initializes wait queues, spinlocks, completions, event list, and RX URBs, submits the URB pool, verifies hardware ID and serial number through control transfers, then registers GPIO/I2C/SPI/ADC hotplug children with handle-specific platform data. Child transfers allocate a response slot, send a USB bulk message with the slot number in `echo`, wait up to 200 ms for the matching RX URB, validate protocol result, copy response data, free the slot, and resubmit the held URB. RX URBs either dispatch events by RCU callback list or complete a waiting transfer slot. Disconnect/suspend stop new transfers, complete waiters, wait for active transfers to drain, and kill URBs.

## State and Persistence
State is volatile and per USB interface: URB buffers, in-flight response contexts, event callbacks, active transfer count, and disconnect flag. No persistent storage exists. Child devices are removed on disconnect.

## Dependencies and Integration Points
The driver depends on USB bulk endpoints, platform MFD children, Linux completions/wait queues/spinlocks/RCU, and `linux/mfd/dln2.h` command definitions used by child drivers. ACPI ADR matching is provided for child functions.

## Risks and Edge Cases
`dln2_rx()` invokes event callbacks while holding `event_cb_lock` and inside an RCU read section; callbacks must not sleep or re-enter registration paths that need the same lock. `dln2_suspend()` calls `dln2_stop()` and sets `disconnect = true`; resume clears it and restarts URBs but does not rerun hardware init or recreate children. Late or malformed responses are dropped and logged. All request slots share a short 200 ms timeout, which may be tight on slow USB paths.

## Test Signals
Test concurrent transfers per handle up to 16 slots, timeout and late-response behavior, disconnect while transfers are active, event callback register/unregister races, suspend/resume transfer recovery, hardware ID rejection, serial-number logging, and child driver transfers through GPIO/I2C/SPI/ADC handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/dln2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ene-kb3930.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ene-kb3930.c

## Purpose
`ene-kb3930.c` is an I2C MFD driver for the ENE KB3930 embedded controller used by the Dell Wyse Ariel platform. It exposes EC RAM through regmap, validates the board model, registers child devices, and optionally provides board power-off/restart signaling through GPIOs.

## Important APIs, Types, and Functions
`struct kb3930` stores the I2C client, EC RAM regmap, and optional off GPIO array. `kb3930_ec_ram_reg_read()` and `kb3930_ec_ram_reg_write()` implement custom regmap access through EC RAM multiplexing registers. `kb3930_off()` drives the off-mode GPIO and generates a 10 Hz shutdown/reset wave forever. `kb3930_restart()` and `kb3930_pm_power_off()` hook into restart and power-off infrastructure. `kb3930_probe()` and `kb3930_remove()` manage lifecycle.

## Control Flow
Probe allocates state, initializes the custom EC RAM regmap, reads `EC_MODEL`, rejects non-`'J'` boards, registers Ariel LED and power child cells, and if the node is a system power controller, obtains two `off-gpios` and installs restart and optional `pm_power_off` handlers. Restart or poweroff calls enter `kb3930_off()` and intentionally never return while toggling the EC wave GPIO.

## State and Persistence
The global `kb3930_power_off` points at the active device for global callbacks. EC RAM is volatile device state exposed by regmap. Power-off mode GPIO state and wave toggling are external board-control signals. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on I2C SMBus word accesses, regmap custom bus callbacks, GPIO descriptors, MFD core, OF system-power-controller detection, Linux restart handlers, and the global `pm_power_off` hook.

## Risks and Edge Cases
Only model `J` is supported. `kb3930_power_off` is a singleton, so multiple EC instances would conflict. If `off-gpios` has fewer than two descriptors, probe fails. Power-off/restart loops forever by design; wrong GPIO wiring can hang without reset or shutdown.

## Test Signals
Validate EC RAM reads for model/version registers, rejection of unknown models, child device creation, off-gpio count validation, restart handler registration/removal, `pm_power_off` ownership behavior, and actual EC shutdown/reset signaling on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ene-kb3930.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/exynos-lpass.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/exynos-lpass.c

## Purpose
`exynos-lpass.c` is the MFD parent for the Samsung Exynos5433 Low Power Audio Subsystem. It maps LPASS top registers, enables the control clock, unmasks selected interrupts, resets internal IP blocks, and populates child devices from device tree.

## Important APIs, Types, and Functions
`struct exynos_lpass` stores the top regmap and `sfr0_ctrl` clock. `exynos_lpass_core_sw_reset()` toggles reset bits. `exynos_lpass_enable()` enables the clock, unmasks SFR/DMA/I2S/UART interrupt paths, and resets I2S, DMA, memory, and UART. `exynos_lpass_disable()` masks interrupts and disables the clock. Probe, runtime PM callbacks, and the devm cleanup action manage lifecycle.

## Control Flow
Probe maps the TOP MMIO resource, gets the SFR clock, creates a 32-bit regmap, marks runtime PM active/enabled, calls `exynos_lpass_enable()`, registers a cleanup action that disables runtime PM and hardware, and finally populates child nodes. Runtime suspend disables the LPASS; runtime resume re-enables and resets it. System sleep uses forced runtime suspend/resume late hooks.

## State and Persistence
State is the regmap pointer and prepared clock. Hardware register state includes interrupt masks and reset lines. The driver does not save register contents; resume re-applies the enable/reset sequence.

## Dependencies and Integration Points
It depends on platform MMIO resources, clock framework, regmap-mmio, runtime PM, OF population, and Exynos PMU register definitions. Child audio IP blocks are instantiated from the device tree under the LPASS node.

## Risks and Edge Cases
`clk_prepare_enable()` return is ignored in `exynos_lpass_enable()`, so clock-enable failure could be hidden. Reset sequencing is fixed and may disturb child state if called while children are active. Interrupt mask semantics are hardware-specific; the code writes bit masks named as unmasked sources.

## Test Signals
Check clock enable/disable counts, TOP regmap access, interrupt mask values after probe/resume, reset toggles for each IP block, runtime suspend/resume with active child drivers, and OF child population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/exynos-lpass.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ezx-pcap.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/ezx-pcap.c

## Purpose
`ezx-pcap.c` is the SPI MFD core for the Motorola PCAP2 ASIC used in EZX phones. It provides serialized register I/O, a cascaded IRQ chip, asynchronous ADC request queueing, and platform-data-defined subdevice registration.

## Important APIs, Types, and Functions
`struct pcap_chip` stores SPI state, I/O lock, IRQ mask state, workqueue/work items, and ADC queue state. Exported register helpers are `ezx_pcap_write()`, `ezx_pcap_read()`, and `ezx_pcap_set_bits()`. IRQ helpers `irq_to_pcap()` and `pcap_to_irq()` map between Linux IRQs and PCAP local IRQs. `pcap_irq_chip`, `pcap_isr_work()`, and `pcap_irq_handler()` implement cascaded interrupts. ADC APIs include `pcap_set_ts_bits()` and `pcap_adc_async()`, with completion in `pcap_adc_irq()`.

## Control Flow
Probe requires platform data, configures 32-bit SPI mode and chip select polarity, initializes locks/work, creates an ordered workqueue, optionally redirects interrupts to the application processor, installs simple IRQ handlers for `PCAP_NIRQS`, masks and clears all PCAP interrupts, chains the parent SPI IRQ, requests the ADC done IRQ, registers platform subdevices, and runs optional board init. The chained handler ACKs the parent and schedules work; work reads mask/status, filters port-2 interrupts, acks serviceable events, dispatches unmasked local IRQs, and repeats while the GPIO line remains asserted. ADC requests are queued in an 8-slot ring and completed by the ADC IRQ callback.

## State and Persistence
Runtime state includes current mask shadow `msr`, queued ADC requests, queue head/tail, and child platform devices. Hardware state includes PCAP registers for IRQ masks/status, ADC configuration, and board-specific init. No persistent storage exists.

## Dependencies and Integration Points
The driver depends on SPI, legacy GPIO APIs, platform data, Linux IRQ core, workqueues, and PCAP register definitions. Child devices are platform-data-defined rather than OF/devm MFD cells.

## Risks and Edge Cases
The driver relies on legacy fixed IRQ bases and platform data. ADC queue size is fixed at eight and returns `-EBUSY` on full slot. IRQ mask/unmask work is asynchronous, so rapid mask changes can lag hardware. Parent IRQ wake is enabled but not disabled in remove. Subdevice creation is manual and cleanup must match all failure paths.

## Test Signals
Validate 32-bit SPI transfers, read/write/set_bits serialization, cascaded IRQ dispatch and mask writes, port-2 filtering, ADC queue full behavior, ADC result channel selection, child device registration/removal, and board init quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/ezx-pcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/fsl-imx25-tsadc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/fsl-imx25-tsadc.c

## Purpose
`fsl-imx25-tsadc.c` is the MFD parent for the Freescale i.MX25 touchscreen/ADC block. It maps the shared register block, configures ADC clocking and power mode, creates a two-entry child IRQ domain, and populates touchscreen/ADC child devices.

## Important APIs, Types, and Functions
`mx25_tsadc_regmap_config` describes the 32-bit MMIO register map. `mx25_tsadc_irq_handler()` demultiplexes GCQ and TCQ interrupt status bits to domain hwirqs 1 and 0. `mx25_tsadc_domain_map()` installs `dummy_irq_chip` with `handle_level_irq`. `mx25_tsadc_setup_irq()` and `mx25_tsadc_unset_irq()` manage the chained parent IRQ and domain. `mx25_tsadc_setup_clk()` computes and writes the ADC divider.

## Control Flow
Probe allocates `struct mx25_tsadc`, maps MMIO, initializes regmap, gets the `ipg` clock, programs an ADC divider that keeps conversion clock under 1.75 MHz, enables the block clock/reset/reference voltage/power-saving mode, creates the child IRQ domain, stores driver data, and populates OF children. Remove unsets the chained IRQ and removes the domain.

## State and Persistence
State is per-device regmap, clock, and IRQ domain. Hardware register state includes clock divider, block enable/reset, power mode, internal reference, and interrupt status. No suspend cache exists.

## Dependencies and Integration Points
It depends on platform MMIO/IRQ resources, regmap-mmio, clock framework, irqdomain, chained IRQ helpers, and OF child population. Child touchscreen and ADC drivers consume the shared regmap and two child IRQ lines through the MFD parent data.

## Risks and Edge Cases
The code reads the clock rate before explicitly enabling the clock; it assumes rate querying works while disabled. Divider calculation floors through hardware-specific behavior below four. The chained handler does not ACK status bits itself, relying on child handling or hardware behavior. `irq_domain_create_simple()` with fixed two entries assumes exactly TCQ and GCQ children.

## Test Signals
Check ADC divider values across IPG rates, register writes for reset/power/reference, child IRQ mapping for hwirqs 0 and 1, chained dispatch for TCQ/GCQ status bits, OF child population, and cleanup on child population failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/fsl-imx25-tsadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/gateworks-gsc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/gateworks-gsc.c

## Purpose
`gateworks-gsc.c` is the I2C MFD core for the Gateworks System Controller. It wraps unreliable I2C accesses with retries, exposes firmware sysfs attributes and timed powerdown, installs a regmap IRQ chip, creates a secondary hwmon I2C client, and populates child devices from device tree.

## Important APIs, Types, and Functions
Exported `gsc_write()` and `gsc_read()` are custom regmap bus callbacks with retry loops for `-EAGAIN` and `-EIO`. `gsc_powerdown()` programs a little-endian sleep duration and sleep control bits. `gsc_show()` and `gsc_store()` implement `fw_version`, `fw_crc`, and `powerdown` sysfs attributes. `gsc_irq_chip` maps eight GSC IRQ bits with inverted ACK semantics. `gsc_probe()` initializes all runtime pieces.

## Control Flow
Probe allocates `struct gsc_dev`, initializes a custom regmap over the I2C client, reads firmware version and CRC, creates a dummy I2C hwmon client at `GSC_HWMON`, installs a low-triggered shared oneshot regmap IRQ chip, logs firmware info, creates sysfs attributes, and populates OF child devices. Remove deletes the sysfs group.

## State and Persistence
State includes firmware version/CRC, primary and hwmon I2C clients, and regmap. Powerdown programming writes persistent controller sleep registers that affect board power. IRQ state is in GSC status/enable registers.

## Dependencies and Integration Points
The driver depends on I2C SMBus byte operations, custom regmap bus, regmap-irq, sysfs, OF platform population, and Gateworks GSC register definitions. Child drivers use the parent regmap and child OF nodes.

## Risks and Edge Cases
`gsc_write()` and `gsc_read()` always return 0 even if the final retry still failed; `gsc_read()` also masks a negative error into an 8-bit value. This can hide I2C failures and corrupt firmware/version or control writes. Sysfs `powerdown` ignores `gsc_powerdown()` errors. The hwmon dummy client is mandatory for probe success.

## Test Signals
Exercise retry behavior under injected `-EAGAIN`/`-EIO`, verify final errors are observable or note current masking, read firmware sysfs values, trigger powerdown register sequence, deliver each regmap IRQ, validate hwmon dummy client creation, and check sysfs cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/gateworks-gsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/hi6421-pmic-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/hi6421-pmic-core.c

## Purpose
`hi6421-pmic-core.c` is the MMIO MFD parent for HiSilicon HI6421 and HI6421V530 PMICs. It creates a regmap over the PMIC register aperture, applies a HI6421 over-current debounce setting, and registers the correct regulator child.

## Important APIs, Types, and Functions
`hi6421_regmap_config` defines 32-bit bus addresses with 4-byte stride and 8-bit values. `of_hi6421_pmic_match` maps compatibles to `enum hi6421_type`. `hi6421_pmic_probe()` performs all setup. `hi6421_devs[]` and `hi6421v530_devs[]` select the regulator child name for each PMIC type.

## Control Flow
Probe gets match data, allocates `struct hi6421_pmic`, maps the MMIO resource, initializes a clockless MMIO regmap, stores driver data, switches by PMIC type, writes over-current debounce/enable bits for HI6421, selects the child cell list, and registers children with `devm_mfd_add_devices()`.

## State and Persistence
Per-device state is the PMIC regmap. Hardware register state includes HI6421 OCP debounce/autostop bits. No explicit persistence or IRQ state is managed by this file.

## Dependencies and Integration Points
The file depends on OF matching, platform MMIO resources, regmap-mmio, MFD core, and Hi6421 PMIC register macros. It integrates mainly with regulator child drivers.

## Risks and Edge Cases
Unknown match data fails probe. OCP debounce setup ignores the return value from `regmap_update_bits()`, so a failed write does not abort. There is no IRQ support here; regulator faults must be handled elsewhere or not at all.

## Test Signals
Probe both compatibles, verify regmap bus address translation, confirm HI6421 OCP debounce bits are written, ensure the correct regulator child appears, and inject MMIO/regmap init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/hi6421-pmic-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/hi6421-spmi-pmic.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/hi6421-spmi-pmic.c

## Purpose
`hi6421-spmi-pmic.c` is the SPMI MFD parent for the HiSilicon Hi6421v600 PMIC. It creates an extended SPMI regmap and registers IRQ and regulator children.

## Important APIs, Types, and Functions
`hi6421v600_devs[]` lists `hi6421v600-irq` and `hi6421v600-regulator` children. `regmap_config` uses 16-bit registers, 8-bit values, full 0xffff range, and `fast_io`. `hi6421_spmi_pmic_probe()` initializes regmap and children. `hi6421_spmi_pmic_driver` binds to `hisilicon,hi6421-spmi`.

## Control Flow
Probe creates a regmap with `devm_regmap_init_spmi_ext()`, stores it as driver data for children, and registers the two MFD children. Failures from child registration are logged and returned.

## State and Persistence
The regmap pointer is device driver data. PMIC state is in SPMI registers and owned by child drivers. No local persistence, IRQ handling, or power management is implemented.

## Dependencies and Integration Points
It depends on the SPMI framework, regmap SPMI extended accessors, MFD core, and child drivers for Hi6421v600 IRQ and regulators.

## Risks and Edge Cases
The parent has no hardware ID validation; compatible matching is trusted. Child drivers must agree on using the parent driver data as a regmap. `fast_io` assumes low-latency serialized access is safe for this bus/provider combination.

## Test Signals
Validate SPMI regmap reads/writes across 16-bit addresses, child creation, child access to parent regmap, OF compatible binding, and failure propagation when regmap or child registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/hi6421-spmi-pmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/hi655x-pmic.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/hi655x-pmic.c

## Purpose
`hi655x-pmic.c` is the MMIO MFD parent for HiSilicon HI655X PMICs. It validates the PMU version, clears local IRQ state, installs a regmap IRQ chip sourced from a GPIO line, and registers power-key, regulator, and clock children.

## Important APIs, Types, and Functions
`hi655x_irqs[]` maps one status register worth of over-temperature, voltage, power-button, and reserved interrupt bits. `hi655x_irq_chip` defines status, ack, and mask bases. `hi655x_regmap_config` describes 32-bit strided MMIO with 8-bit values. `pwrkey_resources[]` maps down/up/hold power-key IRQ resources. `hi655x_local_irq_clear()` clears analog and PMIC IRQ status registers. `hi655x_pmic_probe()` and `hi655x_pmic_remove()` manage lifecycle.

## Control Flow
Probe allocates `struct hi655x_pmic`, maps MMIO, initializes the regmap, reads and validates the version register, clears all local IRQ status/mask state, obtains the optional `pmic` GPIO as input, converts it to an IRQ, installs the regmap IRQ chip with low-triggered no-suspend flags, stores driver data, and registers child devices using the regmap IRQ domain. On child registration failure or remove, it deletes the IRQ chip and removes children.

## State and Persistence
State includes PMIC version, device pointer, regmap, optional GPIO descriptor, and regmap IRQ data. Hardware state includes cleared IRQ status, IRQ masks, and child-controlled regulator/clock registers. No filesystem persistence exists.

## Dependencies and Integration Points
It depends on platform MMIO, regmap-mmio, GPIO descriptors, regmap-irq, MFD core, and Hi655X register macros. Child power-key resources are resolved through the regmap IRQ domain passed to `mfd_add_devices()`.

## Risks and Edge Cases
`devm_gpiod_get_optional()` can return NULL, but `gpiod_to_irq(pmic->gpio)` is called unconditionally; a missing GPIO can fail or crash depending on helper behavior. `regmap_read()` of the version register ignores its return value before validating `pmic->ver`. IRQ clearing writes all ones to multiple status registers, which can drop pending boot events.

## Test Signals
Test supported and unsupported PMU versions, missing/invalid `pmic` GPIO handling, regmap IRQ domain creation, power-key down/up/hold events, local IRQ clear writes, child registration failure cleanup, and no-suspend IRQ behavior during suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/hi655x-pmic.c -->

# sources/distributed-fs/ceph-client/drivers/mfd/intel_soc_pmic_mrfld.c

Purpose: Basin Cove PMIC MFD driver for Merrifield platforms using Intel SCU IPC register access and firmware-provided level2 IOAPIC IRQ resources.

Important APIs/types/functions: `bcove_probe()`, `bcove_ipc_byte_reg_read()`, `bcove_ipc_byte_reg_write()`, `bcove_regmap_config`, `irq_level2_resources`, and child cells for power button, TMU, thermal, BCU, ADC, charger/power source, GPIO, and region.

Control flow: probe allocates `intel_soc_pmic`, obtains SCU IPC handle, initializes a custom IPC-backed regmap, reads seven platform IRQs into static resource entries, and registers all Basin Cove child devices. There is no separate regmap-irq chip because firmware services level1 IRQs.

State and persistence: static IRQ resource array is populated from ACPI/platform IRQs at probe. Register state is in hardware and accessed through SCU IPC byte operations.

Dependencies and integration: ACPI `INTC100E`, SCU IPC device APIs, MFD core, and child drivers named `mrfld_bcove_*`.

Risks: all expected IRQ resources must be present and ordered. Static resources assume a single active device. `devm_intel_scu_ipc_dev_get()` returning NULL is treated as allocation/probe failure, not defer.

Test signals: platform IRQ count/order, IPC regmap reads/writes, child device resources, charger and power-source sharing of IRQ slot 5, and ACPI binding.

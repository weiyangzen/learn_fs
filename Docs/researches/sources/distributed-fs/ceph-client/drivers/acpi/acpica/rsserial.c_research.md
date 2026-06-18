# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsserial.c

Purpose: defines conversion tables for GPIO, pin, clock input, and serial bus resource descriptors, including I2C, SPI, UART, and CSI2 subtypes.

Important APIs, types, and functions: table symbols include `acpi_rs_convert_gpio`, `acpi_rs_convert_clock_input`, `acpi_rs_convert_pin_function`, `acpi_rs_convert_csi2_serial_bus`, `acpi_rs_convert_i2c_serial_bus`, `acpi_rs_convert_spi_serial_bus`, `acpi_rs_convert_uart_serial_bus`, `acpi_rs_convert_pin_config`, `acpi_rs_convert_pin_group`, `acpi_rs_convert_pin_group_function`, and `acpi_rs_convert_pin_group_config`.

Control flow: each table declares fixed header fields, flag bitfields, then variable sections. GPIO and pin descriptors use generic GPIO count/move opcodes for pin tables, resource source or labels, and vendor data. Clock input uses fixed scalar moves plus optional `resource_source`. Serial bus common descriptors move revision/type/slave/producer/sharing/type-data metadata, compute vendor length from subtype-specific minimum data lengths, copy vendor data, compute resource source string length from type data length, and then append subtype-specific fields such as I2C access mode/speed/address, SPI wire mode/polarity/selection/speed, UART flow/stop/data/parity/FIFO/baud, and CSI2 PHY/local port fields.

State and persistence: static conversion metadata only, with variable pointers set into caller-allocated internal resource storage during conversion.

Dependencies and integration points: dispatched through `rsinfo.c` normal and serial subtype tables, interpreted by `rsmisc.c`, sized in `rscalc.c`, and dumped through `rsdumpinfo.c`. This file covers many ACPI 5+/6+ descriptors used by GPIO controllers, pin controllers, camera links, and serial-attached peripherals.

Risks and test signals: variable offsets are dense and descriptor-specific. Incorrect offset/count handling can swap resource source, pin table, labels, or vendor data. Serial subtype sizes must remain consistent with `acpi_gbl_aml_resource_serial_bus_sizes` and `AML_RESOURCE_*_MIN_DATA_LEN`. Tests should round-trip each descriptor with empty and non-empty pin/vendor/source sections, all serial subtypes, boundary string lengths, and invalid subtype dispatch from `rslist.c`.

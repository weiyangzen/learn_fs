# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-reg.h

Purpose: central FlexCop register abstraction header: chip/device/bus enums, I2C/SRAM/DMA enum values, register addresses, endian-specific `flexcop_ibi_value`, and helper macro for read-modify-write bit updates.

Important APIs/types: defines `flexcop_revision_t`, `flexcop_device_type_t`, `flexcop_bus_t`, `flexcop_i2c_port_t`, `flexcop_access_op_t`, SRAM destination/target/type enums, WAN speed enum, DMA indices, and `flexcop_ibi_register`. `flexcop_set_ibi_value(reg, attr, val)` reads a register through local variable `fc`, updates one bitfield, and writes it back.

Control flow: compile-time endian selection includes either `flexcop_ibi_value_le.h` or `flexcop_ibi_value_be.h`, failing if no endian macro is defined.

State/persistence: no runtime state, but it defines the symbolic contract used to manipulate volatile device registers. `extern flexcop_ibi_value ibi_zero` is defined by `flexcop.c`.

Dependencies/integration: included via FlexCop private/common headers by core, I2C, filter, SRAM, EEPROM, frontend, USB, and PCI code.

Risks/test signals: bitfield layout correctness is critical and compiler/endianness sensitive. The macro depends on an in-scope `fc` pointer, which is terse but fragile. Build tests on little- and big-endian targets and register-level tests for representative fields are the main confidence signals.

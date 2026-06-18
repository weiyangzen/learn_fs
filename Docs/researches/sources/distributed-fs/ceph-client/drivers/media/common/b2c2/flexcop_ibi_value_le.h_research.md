# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop_ibi_value_le.h

Purpose: generated little-endian layout for the `flexcop_ibi_value` union, giving named bitfield access to FlexCop IBI registers on little-endian builds.

Important APIs/types: the union mirrors the big-endian file but declares fields in little-endian bit order. It covers DMA descriptors, two-wire/I2C data and status registers, revision/control/IRQ/reset fields, PID and group filters, MAC/card registers, CI/PI/DVB state, SRAM control/buffers/destinations, and WAN speed/chip configuration.

Control flow: no logic; selected by `flexcop-reg.h` when `__LITTLE_ENDIAN` is defined.

State/persistence: represents transient register snapshots and values to write; no durable state.

Dependencies/integration: heavily used by FlexCop filter, I2C, misc, SRAM, reset, EEPROM, frontend, and bus code through `fc->read_ibi_reg`/`write_ibi_reg`.

Risks/test signals: layout errors manifest as wrong hardware behavior rather than type errors. The little-endian path is likely common, so regression signals include real-device I2C transfers, revision detection, PID filtering, MAC programming, SRAM routing, and raw value assertions for representative fields.

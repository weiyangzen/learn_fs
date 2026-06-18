<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2.h -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2.h

Purpose: shared private ABI between AMD MP2 PCI transport and platform adapter drivers.

Important definitions: register offsets define C2P/P2C mailboxes and interrupt registers. `enum i2c_cmd`, `speed_enum`, `mem_type`, `response_type`, and `status_type` encode firmware protocol values. `union i2c_cmd_base` packs command, bus ID, slave address, length, speed, and memory type into a 32-bit command. `union i2c_event` unpacks response/status, memory type, bus ID, length, and address. `struct amd_i2c_common` is per-bus shared command state; `struct amd_mp2_dev` is per-PCI-device state.

Control flow and state: inline runtime PM helpers operate on the PCI device. Function declarations define exported transport operations consumed by the platform driver.

Risks and tests: bitfield layout and enum values are hardware ABI; changing them breaks firmware communication. Test by compiling both MP2 objects together, validating command/event encoding with hardware traces, and exercising all speed and transfer-size modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2.h -->

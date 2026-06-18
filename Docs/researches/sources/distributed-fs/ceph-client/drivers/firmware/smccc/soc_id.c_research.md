# sources/distributed-fs/ceph-client/drivers/firmware/smccc/soc_id.c

## Purpose
`soc_id.c` registers a Linux SoC bus device using ARM SMCCC `ARCH_SOC_ID` data. On arm64 it can also fetch the optional firmware-provided SoC name string introduced in newer SMCCC revisions.

## Important APIs, Types, And Functions
- Bitfield macros extract JEP106 bank, JEP106 ID code, and implementation-defined SoC ID.
- Global objects: `soc_dev` and `soc_dev_attr`.
- arm64 name helpers: `str_fragment_from_reg()` and `smccc_soc_name_init()` copy registers `a1..a17` into a 136-byte NUL-terminated name buffer.
- `smccc_soc_init()` validates SMCCC/SOC_ID support, formats family/soc/revision strings, and registers `soc_device`.
- `smccc_soc_exit()` unregisters and frees state.

## Control Flow
Module init first requires SMCCC version at least 1.2 and a supported SOC_ID version. It rejects negative version or revision returns, allocates `soc_device_attribute`, formats strings such as `jep106:<bank><id>:<soc>`, optionally obtains the machine name via SMCCC 1.2 register invocation, and calls `soc_device_register()`. Exit unregisters the device and frees attributes.

## State And Persistence
The registered SoC device and attribute allocation persist while the module is loaded. String storage uses static buffers for formatted IDs and a read-only-after-init buffer for optional machine name. No data is persisted beyond sysfs exposure.

## Dependencies And Integration Points
It depends on SMCCC discovery state from `smccc.c`, SOC bus infrastructure, bitfield helpers, and arm64 SMCCC 1.2 register invocation for the optional name. The resulting sysfs SoC attributes can be used by userspace and kernel diagnostics.

## Risks
Malformed firmware name strings are ignored if not NUL-terminated within 136 bytes. Negative SOC_ID version/revision returns abort registration. Static formatted string buffers are adequate for one device but reinforce singleton behavior.

## Test Signals
On supported firmware, logs should show ID and revision, and `/sys/devices/soc0` style attributes should include `soc_id`, `family`, `revision`, and optional `machine`. Unsupported firmware should log that ARCH_SOC_ID is not implemented and skip cleanly.

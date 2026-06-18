<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/of.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/of.c

## Purpose
Reads TPM firmware event logs described by Open Firmware/device-tree properties or reserved memory regions.

## Important APIs, Types, And Functions
Key functions are `tpm_read_log_memory_region()` and `tpm_read_log_of()`. It uses `of_reserved_mem_region_to_resource()`, `devm_memremap()`, `of_get_property()`, `of_property_match_string()`, `of_property_read_bool()`, `devm_kmemdup()`, and `__va()`.

## Control Flow
The reader obtains the parent OF node, records `powered-while-suspended` as `TPM_CHIP_FLAG_ALWAYS_POWERED`, and then looks for `linux,sml-size` and `linux,sml-base`. If both are absent, it maps the first reserved-memory region. If exactly one is present, it fails. Physical TPM properties are converted from big endian, while IBM virtual TPM compatibles are treated as already little endian. Nonzero logs are copied or remapped and the format is returned from the TPM version flag.

## State And Persistence
The log pointer and end pointer persist in `chip->log` as devm allocations or mappings. `TPM_CHIP_FLAG_ALWAYS_POWERED` persists on the chip after OF probing and affects suspend logic.

## Dependencies And Integration Points
Used as the final event-log backend. It integrates with PowerPC and OF firmware conventions, reserved memory, TPM virtual-device bindings, and the core TPM suspend path.

## Risks And Edge Cases
Endian handling differs for IBM vTPM versus physical TPM nodes. `__va(base)` assumes the firmware-described log is directly mapped. Mixed presence of size/base is treated as firmware error. Reserved-memory mapping exposes firmware memory directly rather than copying it.

## Test Signals
Exercise IBM physical and virtual TPM device trees, reserved-memory-only descriptions, missing or partial `linux,sml-*` properties, zero-size logs, and suspend behavior when `powered-while-suspended` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/eventlog/of.c -->

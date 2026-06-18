<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/bcm-ocotp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/bcm-ocotp.c

## Purpose
Implements a Broadcom on-chip OTP controller provider with read and write support for v1 and v2 row layouts, using command/status MMIO sequencing.

## Important APIs, Types, And Functions
`struct otpc_map` describes row width and data register offsets; `struct otpc_priv` stores device, base, map, and config. Helpers program command, address, start bit, and data registers. `poll_cpu_status()`, `enable_ocotp_program()`, and `disable_ocotp_program()` manage command completion and write enable sequence. `bcm_otpc_read()` and `bcm_otpc_write()` are NVMEM callbacks; `bcm_otpc_probe()` maps registers, enables CPU mode, reads `brcm,ocotp-size`, selects v1/v2 geometry, and registers NVMEM.

## Control Flow
Probe gets match data from OF or ACPI, maps the controller, enables CPU access, resets start state, validates the size property, adjusts word size to 8 bytes for v2, and registers. Reads issue one READ command per row and copy row words from configured data registers. Writes first send the magic program-enable sequence, then issue PROGRAM commands row by row, and finally disable programming.

## State And Persistence
The provider stores MMIO base and selected layout. OTP bits are one-time persistent hardware state; writes can permanently blow fuses. The static `bcm_otpc_nvmem_config` is mutated during probe for size, dev, priv, and v2 alignment.

## Dependencies And Integration Points
Integrates with OF/ACPI platform matching, NVMEM provider core, Broadcom iProc hardware, and optional cell consumers. DT must provide `brcm,ocotp-size`.

## Risks
Write support is inherently destructive. The static config is shared across instances and could be unsafe for multiple controllers. `disable_ocotp_program()` return is ignored after successful writes. Row-size handling relies on core alignment and correct byte counts.

## Test Signals
Validate v1 and v2 reads, ACPI and OF matches, missing/zero size property failures, write-enable timeout handling, write-prohibited regions, and post-write readback on sacrificial OTP words. Hardware tests should confirm program mode is disabled after errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/bcm-ocotp.c -->

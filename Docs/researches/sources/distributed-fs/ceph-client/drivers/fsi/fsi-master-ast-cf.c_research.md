<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-ast-cf.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-ast-cf.c

## Purpose
`fsi-master-ast-cf.c` implements an FSI master using the ColdFire coprocessor present in AST2400/AST2500 BMCs. It loads `cf-fsi-fw.bin` into reserved memory, patches firmware boot configuration, arbitrates GPIO ownership with the Aspeed GPIO driver, communicates with microcode through SRAM command/status registers, and exposes one FSI link to the core.

## Important APIs, types, and functions
`struct fsi_master_acf` stores the embedded master, SCU regmap, GPIOs and coprocessor GPIO metadata, reserved firmware memory, CVIC mapping, SRAM pool allocation, AST generation flag, external-mode flag, last-address cache, delays, and trace flag. Command construction mirrors the GPIO master with `build_ar_command()`, `build_dpoll_command()`, `build_epoll_command()`, and `build_term_command()`. Coprocessor operations use `do_copro_command()`, `send_request()`, `read_copro_response()`, `handle_response()`, and `fsi_master_acf_xfer()`. Setup/lifecycle functions include `load_copro_firmware()`, `check_firmware_image()`, `fsi_master_acf_setup()`, `fsi_master_acf_terminate()`, and probe/remove.

## Control flow
Probe resolves AST generation, SCU regmap, GPIOs, reserved DRAM, optional CVIC, fixed SRAM allocation, and GPIO coprocessor arbitration hooks. Setup resets ColdFire, clears SRAM, assigns GPIOs to the coprocessor, loads the matching shared/split firmware image, verifies firmware API major version, configures AST-specific memory maps and firmware GPIO/control fields, starts ColdFire, waits for `CF_STARTED`, writes send/echo delays, enables CVIC doorbell when available, then registers the FSI master. Access callbacks build FSI protocol commands, send them to SRAM, ring the coprocessor doorbell, wait for completion, validate CRC, handle ACK/BUSY/ERRA/ERRC, issue D_POLL/E_POLL/TERM as needed, update the last-address optimization, and return data in bus endian format.

## State and persistence behavior
Runtime state spans driver memory, firmware DRAM, SRAM command/status fields, SCU ColdFire mapping registers, GPIO ownership, and last-address/delay caches. The firmware blob is external persistent input, but the driver writes it into reserved memory on setup. External mode stops the coprocessor, returns GPIOs to ARM/external ownership, rescans the bus, and can later restart setup.

## Dependencies and integration points
The driver depends on CRC4, firmware loader, OF reserved memory, genalloc SRAM pools, SCU syscon regmap, Aspeed GPIO coprocessor APIs, optional CVIC, GPIO descriptors, tracepoints, and FSI master APIs. It uses the ABI constants in `cf-fsi-fw.h` and declares `MODULE_FIRMWARE("cf-fsi-fw.bin")`.

## Risks and edge cases
Firmware/header ABI mismatch, reserved-memory alignment, fixed SRAM offset allocation, GPIO arbitration races at startup/shutdown, and coprocessor command timeouts are major risks. Error handling can dump firmware trace data only when trace-enabled firmware is loaded. The last-address optimization must be invalidated on failures, TERM, and BREAK. External mode transitions must serialize against in-flight commands.

## Test signals
Validation should cover AST2400 and AST2500 probe, firmware image selection for shared/split GPIOs, API-version rejection, CVIC interrupt enable, read/write/TERM/BREAK transfers, BUSY and CRC retry paths, external-mode toggling with rescan, GPIO arbitration request/release, and cleanup releasing SRAM and coprocessor GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-ast-cf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.c

## Purpose
`fsi-master-i2cr.c` implements a virtual FSI master behind an IBM I2C Responder (I2CR). The I2CR translates I2C transactions into CFAM/SCOM-style access, so the driver emulates enough CFAM configuration space for FSI engine discovery and forwards engine accesses over I2C.

## Important APIs, types, and functions
Shared exported helpers are `fsi_master_i2cr_read()` and `fsi_master_i2cr_write()`. Internal helpers include parity functions `i2cr_check_parity32()`, `i2cr_check_parity64()`, command builder `i2cr_get_command()`, transaction helper `i2cr_transfer()`, and status checker `i2cr_check_status()`. Master callbacks are `i2cr_read()` and `i2cr_write()`.

## Control flow
Probe allocates `struct fsi_master_i2cr`, chooses a stable master index from the I2C adapter number, initializes a one-link master, and registers it with the FSI core. Core reads below `0xc00` are served from the static `i2cr_cfam` table so the core can discover engines; writes in that range are successful no-ops. Other accesses build parity-protected I2CR commands from CFAM word addresses, perform I2C write/read or write-only transfers under a mutex, check I2CR status/error/log registers, clear error state by writing zeroed command buffers, and convert between FSI big-endian byte expectations and I2CR little-endian wire layout.

## State and persistence behavior
Runtime state is the I2C client pointer, mutex, and registered FSI master. `i2cr_cfam` is static emulated configuration data. I2CR status/error/log registers are cleared after error detection, but no state persists in the driver.

## Dependencies and integration points
It depends on I2C core, OF match `ibm,i2cr-fsi-master`, tracepoints, `fsi-master-i2cr.h`, and FSI master registration. Its exported helpers are also consumed by I2CR-specific clients such as direct I2CR SCOM support.

## Risks and edge cases
The virtual master supports only link 0, slave ID 0, 16-bit local addresses, and 1/2/4 byte accesses. The fake CFAM table must stay consistent with expected FSI discovery behavior. Parity and endian conversions are subtle; mistakes can produce remote I2CR errors. Error clearing uses best-effort I2C sends after status failure.

## Test signals
Probe on an I2C adapter, FSI scan through emulated CFAM space, reads/writes above `0xc00`, parity validation, endian round-trips, status-error trace/log collection, and remove/unregister behavior are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.c -->

# sources/distributed-fs/ceph-client/drivers/scsi/scsi_sysctl.c

## Purpose

`scsi_sysctl.c` registers the SCSI sysctl table under `dev/scsi`. Its only current knob is `logging_level`, which exposes the shared `scsi_logging_level` bitmask used by `scsi_logging.h`.

## Important APIs, types, and functions

`scsi_table[]` is a `struct ctl_table` array containing the `logging_level` entry. The entry points `scsi_init_sysctl()` and `scsi_exit_sysctl()` register and unregister the table. `scsi_table_header` stores the registration handle returned by `register_sysctl()`.

## Control flow

During SCSI subsystem initialization, `scsi_init_sysctl()` calls `register_sysctl("dev/scsi", scsi_table)` and returns `-ENOMEM` if registration fails. During teardown, `scsi_exit_sysctl()` unregisters the saved header. Reads and writes are handled by `proc_dointvec_minmax`, with lower bound `SYSCTL_ZERO` and upper bound `SYSCTL_INT_MAX`.

## State and persistence behavior

The file persists only the sysctl registration header. The exposed value is `scsi_logging_level`, owned by `scsi.c`. Writes through sysctl immediately affect future logging macro decisions and persist until changed or until the module/kernel state is torn down.

## Dependencies and integration points

It depends on Linux sysctl infrastructure, `scsi_logging.h`, and `scsi_priv.h`. It integrates with the logging macros and the same global logging word exposed as a module parameter.

## Risks and edge cases

The upper bound is `INT_MAX`, while the logging word is unsigned and defines bitfields up to bit 29. This is enough for the defined categories but would need review if categories expanded into the sign bit. Teardown assumes `scsi_table_header` was initialized only after successful registration. Disabled `CONFIG_SYSCTL` builds use stubs from `scsi_priv.h`.

## Test signals

Build with `CONFIG_SYSCTL` enabled and disabled. Runtime tests should read and write `/proc/sys/dev/scsi/logging_level`, verify negative values are rejected, and confirm changed bits affect category logging. Init failure injection around `register_sysctl()` should return `-ENOMEM` cleanly.

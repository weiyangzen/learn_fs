# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi.h

## Purpose
`mcdi.h` defines the public MCDI contract for the SFC driver: request states/modes, per-NIC MCDI storage, optional monitor and MTD partition storage, exported firmware command APIs, and the protocol-buffer macro layer used to build and decode `mcdi_pcol.h` command structures.

## Important APIs, Types, And Macros
`enum efx_mcdi_state` models the single command channel: quiescent, running sync, running async, proxy wait, and completed. `enum efx_mcdi_mode` selects poll, event, or fail-fast behavior. `struct efx_mcdi_iface` stores NIC pointer, state, mode, wait queues, `iface_lock`, epoch flag, sequence number, credits, response status/lengths, async queue/timer, optional logging buffer, and proxy authorization fields. `struct efx_mcdi_data` embeds the interface plus optional `struct efx_mcdi_mon` and function flags.

The header declares MCDI lifecycle, RPC, event, reset, firmware-version, board-config, NVRAM, WOL, workaround, privilege-mask, monitor, and optional MTD APIs. The macro layer includes `MCDI_DECLARE_BUF`, `MCDI_PTR`, `MCDI_SET_*`, `MCDI_*`, `MCDI_ARRAY_*`, `MCDI_FIELD`, `MCDI_EVENT_FIELD`, and `efx_has_cap()`.

## Control Flow Role
Command callers declare padded dword buffers, set fields with protocol-name macros, call an MCDI RPC, validate output length, and extract fields with typed helpers. The header defines the state and mode vocabulary used by `mcdi.c` but leaves runtime state transitions to the implementation.

## State And Persistence Behavior
The structs are in-memory driver state initialized during probe and destroyed during removal. They do not persist to disk. APIs declared here may cause persistent firmware effects, especially NVRAM updates, WOL filters, LED settings, and attach/reset state. `struct efx_mcdi_mtd_partition` tracks an update session only for the lifetime of the MTD object.

## Dependencies And Integration Points
`mcdi.h` depends on SFC driver types, Linux synchronization/timer/device types, and protocol constants from `mcdi_pcol.h`. It is included by MCDI core, filters, queue lifecycle, monitor, MAC/PHY, ethtool, reset, and MTD code. Optional stubs make monitor calls compile to no-ops when `CONFIG_SFC_MCDI_MON` is disabled.

## Risks And Edge Cases
The buffer macros enforce many alignment and size assumptions at compile time, but callers still must allocate the right command size and check minimum response lengths before reading arrays. Endianness is mixed: most fields are little-endian MCDI values, while some network fields use explicit big-endian helpers. New fields in `efx_mcdi_iface` require clear locking/barrier rules because it is touched from process, NAPI, and timer contexts.

## Test Signals
Build with monitor, logging, and MTD enabled/disabled. Sparse/endian checking should cover `__force` casts. Protocol changes should trigger `BUILD_BUG_ON` failures when field sizes/alignments drift. Runtime coverage should include minimum and extended response lengths and capability checks through `efx_has_cap()`.

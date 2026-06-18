# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi.h

## Purpose
This header defines the Siena driver's internal MCDI contract: request state and mode enums, protocol context structures, monitor and MTD extension structures, public MCDI transport APIs, event hooks, command helper prototypes, and the macros used to declare, populate, and decode MCDI request/response buffers safely.

## Important APIs, Types, And Functions
- `enum efx_mcdi_state` models the single-request state machine: `QUIESCENT`, synchronous running, asynchronous running, proxy wait, and completed-but-not-consumed.
- `enum efx_mcdi_mode` selects polling, event-driven completions, or fail-fast behavior after severe timeout.
- `struct efx_mcdi_iface` stores NIC association, state, mode, wait queues, locks, sequence/error/response metadata, async queue/timer, optional logging fields, and proxy response wait state.
- `struct efx_mcdi_data` embeds the MCDI interface, optional `struct efx_mcdi_mon`, and function flags returned from firmware attach.
- `struct efx_mcdi_mon` and `struct efx_mcdi_mtd_partition` define shared state for hwmon sensor export and optional MTD flash partitions.
- Accessors `efx_mcdi()` and optional `efx_mcdi_mon()` enforce the expected `efx->mcdi` allocation and return embedded substructures.
- RPC prototypes expose synchronous, quiet, split start/finish, and asynchronous MCDI command paths plus mode switching, async flushing, event processing, reboot polling, reset mapping, and command-specific helpers.
- Buffer macros such as `MCDI_DECLARE_BUF()`, `MCDI_PTR()`, `MCDI_SET_DWORD()`, `MCDI_DWORD()`, `MCDI_SET_QWORD()`, `MCDI_ARRAY_FIELD()`, and `MCDI_EVENT_FIELD()` centralize field offset, alignment, endian, and bitfield access for generated MCDI protocol definitions.

## Control Flow
Most source files include this header, declare stack MCDI buffers with `MCDI_DECLARE_BUF()`, fill fields with the `MCDI_SET_*` and `MCDI_POPULATE_*` macros, call an `efx_siena_mcdi_rpc*()` function, then decode outbuf fields with `MCDI_*` accessors after checking response length. Event paths decode MCDI event qwords with `MCDI_EVENT_FIELD()` and pass events to the handlers declared here.

The state/mode definitions are consumed by `mcdi.c` to serialize callers and by surrounding driver code to switch completion modes when event queues are enabled or disabled. Conditional prototypes and inline stubs make hwmon monitoring disappear when `CONFIG_SFC_SIENA_MCDI_MON` is disabled while preserving call sites.

## State And Persistence
The header declares runtime-only in-memory state. It does not write hardware or persistent storage by itself. Persistent effects happen through functions declared here, especially NVRAM/MTD operations, WOL filters, firmware driver attach/detach, and reset commands implemented in `mcdi.c`. Compile-time state is shaped by `CONFIG_SFC_SIENA_MCDI_LOGGING`, `CONFIG_SFC_SIENA_MCDI_MON`, and `CONFIG_SFC_SIENA_MTD`.

The buffer macros enforce a critical persistence boundary between C structures and firmware ABI: MCDI buffers are dword arrays with explicit little-endian field access rather than native packed C structs. This avoids accidental host layout dependence while matching shared-memory and event formats.

## Dependencies And Integration Points
The header assumes `struct efx_nic`, `struct efx_channel`, `efx_dword_t`, `efx_qword_t`, reset types, LED modes, MTD wrapper types, and generated `MC_CMD_*` constants are available through neighboring Siena headers. It is included by MCDI core code, port/MAC/PHY code, PTP, SR-IOV, hwmon, MTD, board probe, ethtool firmware display, and event processing paths.

It also defines capability helpers, `MCDI_CAPABILITY()`, `MCDI_CAPABILITY_OFST()`, and `efx_has_cap()`, that map generated capability bit names to the NIC type's `check_caps()` implementation. Those helpers tie firmware capability discovery to feature gating elsewhere in the driver.

## Risks And Edge Cases
- The MCDI field macros depend on generated protocol offset and length constants being accurate. Wrong constants or misuse of a field macro on the wrong buffer type will compile but decode incorrect firmware data.
- `_MCDI_CHECK_ALIGN()` catches required alignment at build time for scalar access. New protocol fields with unusual alignment need appropriate array/pointer helpers rather than raw casts.
- `MCDI_VAR_ARRAY_LEN()` subtracts a field offset from the supplied response length; callers must first ensure the response reaches the array offset to avoid size underflow.
- The accessor macros cast byte pointers into `efx_dword_t *` or little-endian scalar pointers. The surrounding comments document that 64-bit MCDI fields are only 32-bit aligned, so users must keep using the split dword qword helpers.
- State enum semantics are part of the concurrency contract. Adding new states or mode transitions requires auditing wait predicates, `cmpxchg()` transitions, and async release logic.
- Conditional inline stubs for hwmon mean call sites cannot infer whether monitoring was actually registered from a successful return unless configuration is known.

## Test Signals
Compile coverage is the primary signal for field-name macros, response-layout constants, and conditional configuration combinations. Runtime signals include successful use of declared RPC APIs by port, PTP, SR-IOV, hwmon, WOL, NVRAM, and reset paths. Tests should exercise buffer macros on 8-, 16-, 32-, and 64-bit fields, variable arrays, event fields, capability checks, build variants with MCDI logging/hwmon/MTD enabled and disabled, and static analysis for invalid pointer aliasing or missing response-length checks before macro reads.

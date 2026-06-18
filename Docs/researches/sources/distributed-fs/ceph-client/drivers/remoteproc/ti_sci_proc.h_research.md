# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_sci_proc.h

## Purpose

This header provides small inline helper wrappers around the TI-SCI processor control protocol for remoteproc drivers. It packages the TI-SCI handle, processor operation table, owning device, processor ID, and handover host ID into `struct ti_sci_proc`, then exposes request, release, handover, configuration, control, and status calls with consistent device-scoped error logging.

## Important APIs, Types, And Functions

`struct ti_sci_proc` stores `sci`, `ops`, `dev`, `proc_id`, and `host_id`. `ti_sci_proc_of_get_tsp()` reads the two-value `ti,sci-proc-ids` device-tree property, allocates the helper with `devm_kzalloc()`, and binds it to `sci->ops.proc_ops`. The remaining inline functions directly wrap TI-SCI processor ops: `request`, `release`, `handover`, `set_config`, `set_control`, and `get_status`.

`ti_sci_proc_set_config()` takes a boot vector and bit masks to set and clear processor configuration flags. `ti_sci_proc_set_control()` changes runtime control flags such as halt/run. `ti_sci_proc_get_status()` returns boot vector, config flags, control flags, and status flags.

## Control Flow

A remoteproc driver first obtains a TI-SCI handle, calls `ti_sci_proc_of_get_tsp()`, and then uses the returned helper through the remote processor lifecycle. The wrappers do no policy work; they forward parameters to firmware and return firmware errors unchanged after logging.

## State And Persistence

The helper object is devm-managed and persists for the owning device lifetime. Hardware and firmware state is not stored in the helper beyond IDs; persistent processor state lives in System Firmware and is read or modified through TI-SCI.

## Dependencies And Integration Points

The header depends on `<linux/soc/ti/ti_sci_protocol.h>` and a DT binding that supplies `ti,sci-proc-ids`. It is used by TI remoteproc drivers such as the K3 R5 driver to avoid open-coded TI-SCI processor operations.

## Risks And Edge Cases

The helper assumes a valid non-NULL TI-SCI handle and proc ops table. A missing or malformed `ti,sci-proc-ids` property returns an error pointer, and all wrappers assume the caller has already checked it. There is no internal serialization; callers must sequence firmware operations correctly.

## Test Signals

Coverage is indirect through remoteproc drivers that request and configure TI-SCI controlled processors. Useful tests include missing property probe failure, request/release error propagation, and boot/control/status sequencing on real or mocked TI-SCI firmware.

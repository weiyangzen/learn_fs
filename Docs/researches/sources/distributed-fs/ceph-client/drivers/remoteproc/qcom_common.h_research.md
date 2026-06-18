# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_common.h

## Purpose

`qcom_common.h` declares shared helper structures and functions for Qualcomm remoteproc platform drivers. It is the local interface for GLINK/SMD transport subdevices, SSR notifier subdevices, PDM auxiliary subdevices, minidump setup, ELF dump segment registration, and optional sysmon integration.

## Important APIs, types, and data

- `struct qcom_rproc_glink` stores a remoteproc subdev, SSR name, device/node references, and a GLINK SMEM edge pointer.
- `struct qcom_rproc_subdev` stores a remoteproc subdev, device/node references, and an SMD edge pointer.
- `struct qcom_rproc_ssr` stores a subdev and private SSR subsystem info pointer.
- `struct qcom_rproc_pdm` stores a subdev, parent device, remoteproc index, and auxiliary device pointer.
- Declared helpers include `qcom_minidump()`, GLINK add/remove, `qcom_register_dump_segments()`, SMD add/remove, SSR add/remove, PDM add/remove, and sysmon add/remove/shutdown-acked helpers.
- When `CONFIG_QCOM_SYSMON` is disabled, sysmon helpers compile to safe stubs.

## Control flow

The header itself has no control flow. Concrete Qualcomm remoteproc drivers embed these structs, call add helpers during probe before `rproc_add()`, and call remove helpers during remove. The remoteproc core later invokes the embedded `rproc_subdev` callbacks installed by `qcom_common.c`.

## State and persistence behavior

The structs are per-rproc lifecycle state holders. They store DT node references, transport edge handles, subsystem info pointers, and auxiliary devices that are valid only between add/remove or prepare/unprepare phases. Sysmon stubs return NULL or false and perform no state changes when the feature is disabled.

## Dependencies and integration points

The header depends on remoteproc core/internal definitions and Qualcomm QMI types. It forward declares GLINK and sysmon types to avoid heavier includes. It is intended for Qualcomm remoteproc drivers that also interact with DT child nodes and the remoteproc subdevice lifecycle.

## Risks and edge cases

- Drivers must keep the embedded helper structs alive for the whole remoteproc lifetime because subdev callbacks reference them by container.
- Remove helpers must match add helpers even when optional DT nodes were absent; the C implementation handles NULL/absent cases, but callers should preserve ordering.
- Sysmon behavior changes at compile time. Callers must tolerate NULL sysmon handles and `false` shutdown-ack results.

## Test signals

Compile with and without `CONFIG_QCOM_SYSMON`. Driver integration tests should ensure each embedded struct is initialized once, add/remove helpers are balanced, optional GLINK/SMD nodes are handled, and sysmon stubs do not break shutdown paths.

# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_common.h

## Purpose
Defines the shared TI K3 remoteproc data structures and function prototypes used by K3 DSP, M4, and related remoteproc drivers.

## Important APIs, Types, And Functions
Defines `KEYSTONE_RPROC_LOCAL_ADDRESS_MASK`, `struct k3_rproc_mem`, `struct k3_rproc_mem_data`, `struct k3_rproc_dev_data`, and `struct k3_rproc`. Prototypes cover mailbox, reset/release, prepare/unprepare, start/stop, attach/detach, loaded resource-table lookup, address translation, internal memory parsing, reserved-memory setup, and TI-SCI processor-handle cleanup.

## Control Flow
No direct control flow is present. SoC-specific wrappers populate `k3_rproc_dev_data`, allocate a remoteproc with `sizeof(struct k3_rproc)` private state, fill TI-SCI/reset/mailbox fields, and assign common callbacks in their `rproc_ops`.

## State And Persistence Behavior
`struct k3_rproc` is persistent per-device private state. It owns pointers to internal memory mappings, reserved memory mappings, mailbox channel/client, reset control, TI-SCI handles, TI-SCI device ID, SoC data, and optional private extension data.

## Dependencies And Integration Points
Included by `ti_k3_common.c`, `ti_k3_dsp_remoteproc.c`, `ti_k3_m4_remoteproc.c`, and related K3 drivers. The header assumes remoteproc, reset, mailbox, TI-SCI, and reserved-memory concepts supplied by the including source files.

## Risks
Structure field changes affect all K3 remoteproc variants. `KEYSTONE_RPROC_LOCAL_ADDRESS_MASK` is declared here but not used by the subset files, so future changes should verify expectations in other K3 drivers.

## Test Signals
Build every K3 remoteproc driver that includes this header and run probe tests that populate all `struct k3_rproc` fields used by common callbacks.

# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_m4_remoteproc.c

## Purpose
Platform driver for TI K3 Cortex-M4F remote processors, currently AM64 M4FSS. It composes K3 common callbacks with AM64 IRAM/DRAM definitions, TI-SCI/reset resources, mailbox, reserved-memory setup, and remoteproc or IPC-only mode detection.

## Important APIs, Types, And Functions
Defines `k3_m4_rproc_ops`, `k3_m4_rproc_probe()`, AM64 memory table `am64_m4_mems`, device data `am64_m4_data`, and compatible `ti,am64-m4fss`. Ops use common prepare/unprepare, start/stop, attach/detach, kick, address translation, and loaded resource table lookup.

## Control Flow
Probe gets match data and firmware name, allocates rproc, disables recovery, fills `struct k3_rproc`, obtains TI-SCI handle/device ID/reset/processor handle, requests processor control, maps internal memories, initializes reserved memory, queries TI-SCI reset and power state, marks `RPROC_DETACHED` when powered for IPC-only mode, requests mailbox, and registers the rproc.

## State And Persistence Behavior
Private K3 state is devm-owned through the platform device. Local reset is used, so prepare/unprepare manage module access and local reset sequencing through common code. Recovery is disabled and IPC-only mode leaves already-powered firmware running.

## Dependencies And Integration Points
Depends on AM64 DT compatible, firmware-name, `ti,sci`, `ti,sci-dev-id`, reset control, resources named `iram` and `dram`, reserved-memory regions, TI-SCI processor control, mailbox, and K3 common implementation. Virtio/rpmsg uses the common mailbox and resource-table path.

## Risks
`r_state` is queried but only `p_state` selects mode, so reset-state nuances do not affect attach versus remoteproc choice. There is no explicit remove callback beyond devm cleanup. Recovery is disabled. AM64 device data sets boot alignment, but this file uses common start directly and does not validate alignment.

## Test Signals
Test AM64 probe with valid and missing resources, TI-SCI errors, reserved-memory setup, mailbox request failures, remoteproc boot/stop with local reset, IPC-only attach when powered, firmware-name parsing, IRAM/DRAM translation, rpmsg traffic, and driver unbind while running or attached.

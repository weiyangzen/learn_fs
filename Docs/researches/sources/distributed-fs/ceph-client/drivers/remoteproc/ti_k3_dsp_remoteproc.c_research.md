# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_dsp_remoteproc.c

## Purpose
Platform driver for TI K3 C66, C71, and C7xV DSP remote processors. It binds DSP-specific memory definitions to the K3 common layer, programs DSP boot address through TI-SCI processor control, supports remoteproc-managed and IPC-only modes, and registers with remoteproc core.

## Important APIs, Types, And Functions
Defines `k3_dsp_rproc_start()`, `k3_dsp_rproc_probe()`, `k3_dsp_rproc_remove()`, `k3_dsp_rproc_ops`, memory tables `c66_mems`, `c71_mems`, `c7xv_mems`, and matching device data. Compatibles include `ti,j721e-c66-dsp`, `ti,j721e-c71-dsp`, `ti,j721s2-c71-dsp`, and `ti,am62a-c7xv-dsp`.

## Control Flow
Probe obtains match data and firmware name, allocates rproc, disables recovery, conditionally installs common prepare/unprepare for local-reset devices, requests mailbox, obtains TI-SCI handle/device ID/reset/processor handle, requests processor control, maps internal memories, initializes reserved memory, queries initial power state, chooses detached IPC-only mode when already powered, then registers the rproc.

Start checks boot-address alignment against SoC data, programs TI-SCI processor config with that boot address, and then calls common `k3_rproc_start()` to release reset. Remove detaches only if the remoteproc is currently attached.

## State And Persistence Behavior
Per-device state is `struct k3_rproc` in `rproc->priv`, with devm-managed resources. Recovery is disabled. IPC-only mode leaves the DSP running and uses attach/detach NOPs plus the loaded resource table from reserved memory.

## Dependencies And Integration Points
Depends on TI-SCI processor/device ops, reset control, OMAP mailbox, named internal memory resources, reserved memory, and K3 common helpers. Virtio/rpmsg integration flows through common mailbox and resource-table handling.

## Risks
Boot alignment differs by DSP family and invalid firmware entry points fail before reset release. The ops table relies on core default ELF callbacks. Recovery is disabled and common crash mailbox handling only logs. IPC-only mode depends on TI-SCI power state accurately reflecting externally booted firmware.

## Test Signals
Test all compatibles and memory tables, missing firmware-name, TI-SCI/reset/processor-control failures, boot-address alignment failures, remoteproc boot/stop, IPC-only attach/detach, reserved-memory resource-table discovery, mailbox rpmsg traffic, and remove while attached.

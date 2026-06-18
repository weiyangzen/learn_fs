# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_idc.c

## Purpose
`idpf_idc.c` implements the IDPF Inter-Driver Communication integration used to expose RDMA-capable IDPF devices and vports as Linux auxiliary devices. It creates and removes core and per-vport auxiliary devices, passes mapped LAN register and MSI-X resources to the RDMA auxiliary driver, emits MTU/reset events, and exports callbacks that the RDMA side uses to bring vport devices up/down or request a reset.

## Important APIs, types, and functions
- Initialization and teardown: `idpf_idc_init()`, `idpf_idc_init_aux_core_dev()`, `idpf_idc_deinit_core_aux_device()`, and `idpf_idc_deinit_vport_aux_device()`.
- Auxiliary-device plumbing: `idpf_plug_core_aux_dev()`, `idpf_plug_vport_aux_dev()`, `idpf_unplug_aux_dev()`, `idpf_core_adev_release()`, and `idpf_vport_adev_release()`.
- Vport RDMA lifecycle: `idpf_idc_init_aux_vport_dev()`, `idpf_idc_vport_dev_up()`, `idpf_idc_vport_dev_down()`, and exported `idpf_idc_vport_dev_ctrl()`.
- Event and reset integration: `idpf_idc_vdev_mtu_event()`, `idpf_idc_issue_reset_event()`, and exported `idpf_idc_request_reset()`.
- Resource handoff: `idpf_idc_init_msix_data()` and the construction of `iidc_rdma_priv_dev_info::mapped_mem_regions`.

## Control flow
`idpf_idc_init()` is called after core device initialization and returns success when RDMA is unsupported or the device ops table has no IDC initializer. When RDMA is enabled, the device-specific `idc_init` callback typically builds the core auxiliary device through `idpf_idc_init_aux_core_dev()`. That function allocates `iidc_rdma_core_dev_info` and private info, records PF/VF function type, captures BAR LAN register mappings from `adapter->hw.lan_regs`, attaches RDMA MSI-X entries if available, and registers an auxiliary device named from the PCI vendor and `.rdma.core` suffix.

When the RDMA core auxiliary driver is ready, it calls exported `idpf_idc_vport_dev_ctrl(cdev_info, true)`. The IDPF side iterates allocated vports; for each RDMA-enabled vport it either allocates `iidc_rdma_vport_dev_info` from the virtchnl create-vport flags or re-plugs an existing vport auxiliary device, then registers a `.rdma.vdev` auxiliary child. When the RDMA core goes down, `idpf_idc_vport_dev_ctrl(..., false)` removes each vport auxiliary device but retains vport info for possible replug.

MTU soft resets call `idpf_idc_vdev_mtu_event()` before and after the change. The function locks the auxiliary device, verifies a bound driver, derives the RDMA auxiliary driver container, and calls its event handler with the selected event bit. Hard reset preparation similarly calls `idpf_idc_issue_reset_event()` for the core auxiliary device. RDMA-triggered reset requests call exported `idpf_idc_request_reset()`, set `IDPF_HR_FUNC_RESET` if no reset is already active, and queue `vc_event_task`.

Teardown paths unregister auxiliary devices with `auxiliary_device_delete()` and `auxiliary_device_uninit()`, free IDs from a file-local `IDA`, and release allocated IDC core/vport structures.

## State and persistence behavior
The persistent IDC state is stored on `adapter->cdev_info` and `vport->vdev_info`. Core private data contains function type, mapped register regions, RDMA protocol, PCI device, and optional RDMA MSI-X entries. Vport info contains vport ID, netdev, parent core auxiliary device, and the current auxiliary device pointer. The file does not persist hardware configuration; it publishes existing IDPF resources to another kernel driver. Auxiliary device IDs are allocated from a global `DEFINE_IDA`.

## Dependencies and integration points
This file depends on Linux auxiliary bus, IDA allocation, PCI driver data, IDPF virtchnl create-vport data, and `iidc_rdma_*` structures from the IDC/RDMA interface. It integrates with `idpf_lib.c` reset and MTU flows, with `idpf_main.c` remove/deinit through core/vport cleanup, and with device-specific ops that initialize IDC only for RDMA-capable hardware.

## Risks and edge cases
- The auxiliary device `name` is assigned from a stack buffer in both plug helpers. If `auxiliary_device_init/add` does not copy the name synchronously, this is a lifetime hazard and should be verified against auxiliary bus semantics.
- `idpf_idc_vport_dev_up()` returns only the last error observed while iterating vports; earlier failures can be overwritten by later success.
- Event delivery locks the device and checks `adev->dev.driver`, but concurrent unplug paths still require careful ordering to avoid use-after-free.
- Resource maps expose BAR virtual addresses and MSI-X entries to another driver; stale pointers after reset/remove would be high impact.
- RDMA reset requests are coalesced by reset-in-progress checks; tests should confirm repeated requests do not lose required state.

## Test signals
Build with RDMA/auxiliary support enabled, probe RDMA-capable PF/VF devices, confirm core and vport auxiliary devices appear and disappear on RDMA driver bind/unbind, validate mapped register region counts and MSI-X counts, exercise MTU changes and observe before/after RDMA events, request resets from the RDMA side, unload while auxiliary devices are bound, and run reset/remove races under KASAN/KCSAN or lockdep.

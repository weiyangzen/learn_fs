# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/auxbus.c

## Purpose
`auxbus.c` exposes AMD/Pensando core services to auxiliary client drivers. It registers clients with firmware, unregisters them, wraps client AdminQ commands in core AdminQ requests, and creates/deletes Linux `auxiliary_device` instances for supported virtual interface types such as firmware-control and vDPA.

## Important APIs, Types, And Functions
Exported APIs are `pds_client_register`, `pds_client_unregister`, and `pds_client_adminq_cmd`, which auxiliary clients can call after binding. `pdsc_auxbus_dev_add` and `pdsc_auxbus_dev_del` are internal core helpers used by PF/VF probe, remove, SR-IOV, devlink enable toggles, and reset handling. `pdsc_auxbus_dev_register` allocates `struct pds_auxiliary_dev`, fills `vf_pdev` and `client_id`, initializes `auxiliary_device`, and adds it. `pdsc_auxbus_dev_release` frees the wrapper when the aux device lifetime ends.

## Control Flow
Client registration posts `PDS_AQ_CMD_CLIENT_REG` with a device name and expects a nonzero firmware `client_id`. Unregistration posts `PDS_AQ_CMD_CLIENT_UNREG`. Client command forwarding resolves the PF from the VF PCI device through `pci_physfn`, wraps the supplied request into `PDS_AQ_CMD_CLIENT_CMD`, copies a bounded payload into `client_cmd`, and posts it through `pdsc_adminq_post`, optionally fast-polling.

Aux-device creation starts in `pdsc_auxbus_dev_add`. It validates the client function pointer and VIF type, takes the PF `config_lock`, rejects add when the client function is firmware-dead or stopping, checks firmware-reported VIF support plus runtime enablement, registers the client with firmware, then creates the aux device. If auxiliary-device add fails, it unregisters the client ID. Deletion takes the same lock, unregisters the client, deletes/uninitializes the auxiliary device, and clears the caller's pointer.

## State And Persistence
The persistent runtime state is `struct pds_auxiliary_dev` and the stored `client_id` returned by firmware. PF `vfs[]` entries and `pdsc->padev` hold pointers to active aux devices. VIF support/enablement comes from `pdsc->viftype_status` and `pdsc->dev_ident.vif_types`. There is no disk persistence.

## Dependencies And Integration Points
This file integrates with Linux PCI PF/VF helpers, the auxiliary bus, `pds_auxbus.h`, core AdminQ posting, PF `config_lock`, firmware VIF identity, and exported GPL symbols consumed by client drivers. It is called from `main.c` for PF/VF lifecycle and from `devlink.c` when runtime enable parameters change.

## Risks
Client registration is intentionally done before `auxiliary_device_add` so a probing aux client can issue AdminQ commands, but this makes cleanup ordering important on add failure. `pds_client_adminq_cmd` assumes the PF driver data is valid and available through the VF's physical function. Feature disable loops in devlink can leave some VFs updated before a later add error is returned. Reset/remove paths must delete aux devices before tearing down AdminQ so clients can clean up through firmware.

## Test Signals
Validate aux device creation and deletion on PF probe/remove, VF probe/remove, SR-IOV enable/disable, devlink `enable_vnet` toggles, firmware not supporting a VIF type, firmware returning null client ID, and client AdminQ command forwarding with and without fast-poll.

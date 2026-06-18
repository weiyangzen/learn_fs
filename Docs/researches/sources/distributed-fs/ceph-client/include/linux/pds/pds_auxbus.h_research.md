<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_auxbus.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_auxbus.h

## Purpose
Defines the PDS auxiliary bus device wrapper used to expose PF-managed services to auxiliary client drivers. It binds an `auxiliary_device` to the VF PCI device and the firmware-assigned PDS client ID.

## Important APIs, Types, And Functions
- `struct pds_auxiliary_dev` contains `struct auxiliary_device aux_dev`, `struct pci_dev *vf_pdev`, and `u16 client_id`.
- `pds_client_adminq_cmd()` submits a client AdminQ command on behalf of an auxiliary device, taking request/response AdminQ unions, request length, and flags.

## Control Flow
The PDS core creates or registers an auxiliary device, associates it with a VF PCI device and `client_id`, then auxiliary drivers call `pds_client_adminq_cmd()` to proxy AdminQ requests through the core. The core can wrap the request in a client command and return the firmware completion.

## State And Persistence
The persistent state in this header is the auxiliary-device identity and the assigned `client_id`. Request and response buffers are per-call transient state. Lifetime is tied to the Linux auxiliary bus device model and the parent PCI device.

## Dependencies And Integration Points
Includes `<linux/auxiliary_bus.h>` and relies on PDS AdminQ unions from the broader PDS headers. It integrates with auxiliary drivers for vDPA, VFIO/live migration, firmware control, or other PDS clients that must share the PF AdminQ path.

## Risks And Edge Cases
Risks include stale `client_id` after unregister/reset, using the helper after the auxiliary device has been removed, passing an incorrect `req_len` for a union member, and lifetime races with the VF PCI device. Error propagation from firmware status to client drivers is an important integration boundary.

## Test Signals
Exercise auxiliary-device probe/remove, client command submission, PF reset while clients are active, invalid request length handling, and client unregister paths. Successful vDPA/VFIO/fwctl auxiliary workflows are end-to-end validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_auxbus.h -->

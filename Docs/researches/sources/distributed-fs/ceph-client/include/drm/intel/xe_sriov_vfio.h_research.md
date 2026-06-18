# sources/distributed-fs/ceph-client/include/drm/intel/xe_sriov_vfio.h

Purpose: declares the interface used by VFIO migration code to coordinate Intel Xe SR-IOV virtual function control through the physical function driver.

Important APIs/types/functions: functions obtain a PF `xe_device` from a VF `pci_dev`, check migration support, prepare/wait for FLR, suspend/resume a VF, enter/exit stop-copy save, enter/exit resume-data restore, move a VF to error state, read/write migration data to userspace buffers, and estimate stop-copy data size.

Control flow: VFIO asks for the PF object, validates migration support, coordinates FLR, then drives migration state transitions. Stop-copy and resume-data phases bracket streaming reads/writes of migration payloads; failures can move the VF into an error state requiring reset.

State and persistence: migration, suspend, FLR pending/done, and error states are maintained in PF/VF driver and firmware state outside this header. Userspace buffers carry transient migration data.

Dependencies and integration: depends on PCI, Xe device, Linux types, and `char __user` user-memory pointers. Integrated by Xe SR-IOV PF code and VFIO PCI migration support.

Risks and test signals: VF ID 0 is invalid, user-copy paths must handle partial read/write and errno, and state-transition ordering matters. Test VF migration happy path, FLR timeout, suspend/resume across all tiles, partial data streaming, unsupported migration, and error-state recovery.

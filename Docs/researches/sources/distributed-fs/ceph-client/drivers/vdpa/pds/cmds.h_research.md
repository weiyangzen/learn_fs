<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.h

Purpose: Declares the PDS vDPA admin command wrapper interface consumed by the vDPA device implementation.

Important APIs: Prototypes cover hardware init/reset/status, MAC and max VQ pair attributes, and VQ init/reset commands carrying `struct pds_vdpa_vq_info`.

Control flow: `vdpa_dev.c` includes this header and calls the wrappers at lifecycle boundaries: `dev_add`, `set_status`, `reset`, and `set_vq_ready`.

State and persistence: No state in the header. It defines the command interface that mutates firmware state and updates VQ indices through pointer arguments.

Dependencies and integration points: Requires visible declarations of `struct pds_vdpa_device` and `struct pds_vdpa_vq_info` from `vdpa_dev.h`.

Risks: Prototype drift from command implementation or caller expectations would cause compile failures or ABI misuse. Invert index arguments must be supplied consistently for packed-ring queues.

Test signals: Full PDS module build validates prototypes; queue lifecycle tests validate caller/command contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/cmds.h -->

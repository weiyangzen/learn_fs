# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_stream2mmio_rmgr.h

Purpose: private state model for stream2mmio SID allocation.

Important type: `isys_stream2mmio_rsrc_t` holds an active SID bitmap and active counter.

Control flow/state: no executable logic; implementation maintains one instance per stream2mmio block.

Dependencies/integration: tied to stream2mmio hardware constants and virtual ISYS channel descriptors.

Risks: no owner metadata and fixed bitmap width. Any change in hardware SID range must be reflected in the implementation and tests.

Test signals: active-table/counter invariants, maximum SID boundary, and reset state after init/uninit.

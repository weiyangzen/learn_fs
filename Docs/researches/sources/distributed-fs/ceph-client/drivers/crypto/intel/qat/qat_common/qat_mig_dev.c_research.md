# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_mig_dev.c

Purpose: exposes a small exported wrapper API for QAT VF migration devices. It maps a parent PCI device to an ADF accelerator, validates that the hardware supplies a full `qat_migdev_ops` table, stores VF identity, and forwards lifecycle/state-transfer calls.

Important APIs and functions: `qat_vfmig_create()` allocates `struct qat_mig_dev` and validates required ops. `qat_vfmig_init()`, `cleanup()`, `reset()`, `open()`, `close()`, `suspend()`, `resume()`, `save_state()`, `save_setup()`, `load_state()`, and `load_setup()` dispatch through `GET_VFMIG_OPS(accel_dev)`. `qat_vfmig_destroy()` frees the wrapper. All are exported GPL symbols.

Control flow: users first call create with PF `pci_dev` and VF id. The wrapper stores `parent_accel_dev`; subsequent calls fetch migration ops from that parent each time and call the matching function. There is no internal sequencing beyond create-time ops validation.

State and persistence: persistent state is only `vf_id` and `parent_accel_dev` inside `qat_mig_dev`; migration buffers and device state are owned by device-specific ops. The object lifetime is explicit and heap allocated.

Dependencies and integration points: integrates with `adf_devmgr_pci_to_accel_dev()`, ADF hardware data migration ops, and the public `<linux/qat/qat_mig_dev.h>` interface used by migration/vfio code.

Risks and test signals: after create, ops are assumed stable and non-NULL; hot-unplug or hw-data teardown must not race with callers. There is no argument validation for NULL `mdev` in forwarding functions. Tests should cover missing op rejection, parent lookup failure, VF id propagation, each forwarded op, error propagation, and lifecycle ordering around cleanup/destroy.

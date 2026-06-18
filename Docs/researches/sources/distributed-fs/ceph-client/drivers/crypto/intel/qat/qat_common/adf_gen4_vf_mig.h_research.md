## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_vf_mig.h

Purpose: Declares the Gen4 VF migration ops initializer.

Important APIs/types: Includes `adf_accel_devices.h` and declares `void adf_gen4_init_vf_mig_ops(struct qat_migdev_ops *vfmig_ops);`.

Control flow/state: No state is stored. The implementation installs all lifecycle, suspend/resume, setup, and state save/load callbacks into the supplied ops table.

Dependencies/integration: Used by Gen4 product drivers that expose VF migration support.

Risks and test signals: Build coverage should ensure migration-capable products include this header and link the implementation. Runtime validation is through the ops table installed by this single entry point.

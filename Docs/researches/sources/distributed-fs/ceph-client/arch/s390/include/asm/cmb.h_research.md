<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cmb.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cmb.h

Purpose: Declares channel-measurement facility operations for CCW devices.

Important APIs/types/functions: `enable_cmf()`, `disable_cmf()`, `__disable_cmf()`, `cmf_read()`, and `cmf_readall()`. Source-visible declarations include: #define S390_CMB_H; struct ccw_device;; extern int enable_cmf(struct ccw_device *cdev);; extern int disable_cmf(struct ccw_device *cdev);; extern int __disable_cmf(struct ccw_device *cdev);; extern u64 cmf_read(struct ccw_device *cdev, int index);; extern int cmf_readall(struct ccw_device *cdev, struct cmbdata *data);.

Control flow: Drivers enable measurement collection for a CCW device, read individual counters or full `cmbdata`, and disable collection on teardown.

State and persistence behavior: Persistent state lives in channel measurement blocks and CCW device measurement configuration.

Dependencies and integration points: Direct includes are #include <uapi/asm/cmb.h>. Integrated with Integrates CCW devices, performance accounting, and channel subsystem measurement support..

Risks: Measurement enable/disable must be synchronized with device lifetime to avoid reading freed or stale CMB data.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 14 lines, 425 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cmb.h -->

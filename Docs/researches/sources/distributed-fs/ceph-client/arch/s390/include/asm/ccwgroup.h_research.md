<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwgroup.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwgroup.h

Purpose: Declares grouped CCW device support for multi-subchannel logical devices.

Important APIs/types/functions: `ccwgroup_device`, `ccwgroup_driver`, device states, online/offline registration helpers, and root-device creation/removal APIs. Source-visible declarations include: #define S390_CCWGROUP_H; struct ccw_device;; struct ccw_driver;; struct ccwgroup_device {; enum {; struct mutex reg_mutex;; unsigned int count;; struct device dev;; struct work_struct ungroup_work;; struct ccw_device *cdev[];.

Control flow: A group driver binds several `ccw_device` instances into one device-model object, manages online/offline transitions, and routes callbacks through the group driver.

State and persistence behavior: State persists in group device membership arrays, driver data, online state, and device-model references.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates qeth and other grouped CCW drivers, driver core, sysfs, and CCW bus matching..

Risks: Reference management and partial online failures are risky because multiple subchannels must transition consistently.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 75 lines, 2300 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwgroup.h -->

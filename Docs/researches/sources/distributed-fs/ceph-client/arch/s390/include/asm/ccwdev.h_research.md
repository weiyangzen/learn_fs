<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwdev.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwdev.h

Purpose: Declares the public CCW device and driver API for the s390 channel subsystem.

Important APIs/types/functions: `ccw_device_id`, `ccw_device`, `ccw_driver`, match helpers, online/offline/start/halt/clear/resume APIs, options flags, DMA helpers, console helpers, and path/query helpers. Source-visible declarations include: #define _S390_CCWDEV_H_; struct irb;; struct ccw1;; struct ccw_dev_id;; #define CCW_DEVICE(cu, cum) \; #define CCW_DEVICE_DEVTYPE(cu, cum, dev, devm) \; static inline const struct ccw_device_id *; struct ccw_device {; struct ccw_device_private *private; /* cio private information */; struct mutex reg_mutex;.

Control flow: Drivers register ID tables and callbacks, the CSS bus matches devices, and CCW/TM start helpers issue channel programs or transport-control words with interruption parameters and path masks.

State and persistence behavior: Persistent state is `ccw_device` private CSS state, locks, online flags, path state, DMA allocations, and driver registration.

Dependencies and integration points: Direct includes are #include <linux/device.h>, #include <linux/mod_devicetable.h>, #include <asm/chsc.h>, #include <asm/fcx.h>, #include <asm/irq.h>, #include <asm/schid.h>, #include <linux/mutex.h>. Integrated with Integrates channel subsystem core, device model, DASD/tape/net CCW drivers, console devices, DMA pools, FCX/TCW support, and CHSC path queries..

Risks: Path masks, interruption parameters, forced starts, and DMA ownership are hardware-facing; bad lifetimes can wedge subchannels or corrupt DMA.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 238 lines, 8532 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/ccwdev.h -->

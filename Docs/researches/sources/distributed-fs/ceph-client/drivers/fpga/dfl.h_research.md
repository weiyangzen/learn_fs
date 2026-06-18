# sources/distributed-fs/ceph-client/drivers/fpga/dfl.h

Purpose: internal header for the DFL framework and DFL-aware drivers. It centralizes DFH/FME/Port register definitions, feature IDs, bit masks, core data structures, inline helpers, and exported prototypes used by `dfl.c`, PCI enumeration, FME/port drivers, private-feature drivers, and SR-IOV/IRQ helpers.

Important APIs and types: register definitions cover common DFH fields, DFHv1 CSR and parameter records, FME capability/port-offset/error registers, and Port capability/control/status/error/user-interrupt registers. Key structures include `dfl_fpga_port_ops`, `dfl_feature_id`, `dfl_feature_driver`, `dfl_feature_irq_ctx`, `dfl_feature`, `dfl_feature_dev_data`, `dfl_feature_platform_data`, `dfl_feature_ops`, `dfl_fpga_enum_info`, `dfl_fpga_enum_dfl`, and `dfl_fpga_cdev`. Inline helpers implement feature-use accounting, private-data access, feature iteration, feature lookup by ID, conversion from inode/device to DFL data, parent lookup, and FME/Port DFH detection.

Control flow role: the header itself has no runtime entry point, but it defines the contracts that make DFL enumeration multi-stage. Parent bus drivers create `dfl_fpga_enum_info`; the core creates `dfl_feature_dev_data`; platform drivers bind to FME/port devices and initialize subfeatures through `dfl_feature_driver` and `dfl_feature_ops`; private subfeatures may become `struct dfl_device` instances on the DFL bus.

State and persistence: no storage is allocated in the header, but it describes all major in-memory state fields, including open/exclusive-use tracking, port disable counts, platform resources, IRQ eventfd contexts, FPGA-region container links, and released-port counters. Hardware-persistent state is represented only as register offsets and masks.

Dependencies and integration points: depends on Linux bitfield, cdev, eventfd, interrupt, iopoll, platform-device, UUID, and FPGA region headers. It is tightly coupled to the DFL ABI in `<linux/dfl.h>` and the register layout understood by Intel FPGA hardware.

Risks and test signals: risks include duplicated hardware constants becoming stale, inline use-count helpers requiring external locking, `dfl_get_feature_ioaddr_by_id` warning and returning NULL when callers assume presence, and global assumptions such as `MAX_DFL_FPGA_PORT_NUM` being four. Test signals are compile coverage across DFL core and drivers, successful modalias matching, correct register decoding on hardware, and SR-IOV/IRQ workflows using the declared APIs without lockdep or lifetime warnings.

# sources/distributed-fs/ceph-client/include/scsi/fcoe_sysfs.h

Purpose: Declares sysfs-facing FCoE controller and FCF device models plus driver callbacks for exposing link-error counters, mode/enabled state, selected FCF, and VLAN.

Important APIs/types/functions: `struct fcoe_sysfs_function_template` contains get/set callbacks. `struct fcoe_ctlr_device` embeds a `struct device`, callback template, FCF list, workqueues, mutex, dev-loss timeout, mode, enabled state, and LESB counters. `struct fcoe_fcf_device` represents a discovered FCF with device, peer list, delete/devloss work, state, fabric/switch names, FC map, VFID, MAC, priority, FKA period, selected flag, and VLAN. Add/delete/setup/teardown APIs manage devices.

Control flow and state: Controller and FCF devices are registered under sysfs and updated by FCoE control-plane code. Workqueues process deletion and dev-loss events. Inline helpers map `struct device` back to controller/FCF and private data.

Dependencies and integration: Depends on Linux device model, workqueues, mutexes, Ethernet addresses, and FCoE LESB structures. Used by FCoE transport and management tooling.

Risks and test signals: Risks include device lifetime races, devloss delayed-work ordering, stale sysfs attributes, missing parent linkage, and host-order counter assumptions. Tests should cover add/delete, sysfs read/write callbacks, FCF devloss, mode/enabled transitions, and teardown with pending work.

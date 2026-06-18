# sources/distributed-fs/ceph-client/include/xen/xenbus.h

## Purpose
`xenbus.h` declares the Linux Xenbus driver/device API used to discover Xenstore devices, register frontend/backend drivers, read and write Xenstore nodes, manage watches and transactions, transition states, set up grant rings and event channels, and expose xenbus device files.

## Important APIs, Types, and Functions
Key types are `struct xenbus_watch`, `struct xenbus_device`, `struct xenbus_device_id`, `struct xenbus_driver`, and `struct xenbus_transaction`. Important APIs include `xenbus_register_frontend/backend`, `xenbus_unregister_driver`, `xenbus_directory/read/write/exists/rm`, transaction start/end, `xenbus_scanf`, `xenbus_read_unsigned`, `xenbus_printf`, `xenbus_gather`, store notifiers, watch registration, suspend/resume hooks, `xenbus_switch_state`, ring setup/map/unmap helpers, event-channel allocation/free, state reading, and error/fatal reporting.

## Control Flow
Drivers register with the Xenbus core, probe devices discovered in Xenstore, read peer details, set up grant rings and event channels, switch to connected state, and react to peer state changes through watches. Xenstore operations can be grouped in transactions; suspend/resume pauses and restores store communication and watches.

## State and Persistence Behavior
`struct xenbus_device` tracks device path, peer path/id, current state, watches, work, completions, reclaim semaphore, and event statistics. Xenstore nodes persist outside the kernel in xenstored; ring mappings and event channels persist until teardown.

## Dependencies and Integration Points
It depends on Linux device model, notifier, mutex, completion, fs, semaphore, Xen grant table, Xenstore wire protocol, Xenbus state UAPI, and event channels. It is the main integration point for Xen block, net, console, balloon, SCSI, and custom frontend/backend drivers.

## Risks and Test Signals
Risks include transaction retry omissions, watch callback races, peer-state deadlocks, grant ring leaks, event-channel leaks/spurious events, suspend/resume watch loss, and failing to handle vanished devices. Test signals include frontend/backend probe/remove, Xenstore transaction conflict handling, watch queue behavior, ring setup teardown, event-channel allocation, and state-machine error paths.

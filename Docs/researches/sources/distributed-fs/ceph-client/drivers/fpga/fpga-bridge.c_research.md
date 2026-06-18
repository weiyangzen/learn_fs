# sources/distributed-fs/ceph-client/drivers/fpga/fpga-bridge.c

Purpose: generic FPGA bridge class and helper library. It registers bridge devices, exposes their name/state through sysfs, provides exclusive get/put semantics, and lets FPGA regions disable and re-enable one or more bridges around reconfiguration.

Important APIs and functions: exported operations include `fpga_bridge_enable`, `fpga_bridge_disable`, `of_fpga_bridge_get`, `fpga_bridge_get`, `fpga_bridge_put`, `fpga_bridges_enable`, `fpga_bridges_disable`, `fpga_bridges_put`, `of_fpga_bridge_get_to_list`, `fpga_bridge_get_to_list`, `__fpga_bridge_register`, and `fpga_bridge_unregister`. `struct fpga_bridge` instances are registered under the `fpga_bridge` class with IDA-assigned IDs and optional low-level ops groups. `__fpga_bridge_get` stores image info, locks the bridge mutex, and takes the owner module reference.

Control flow: low-level bridge drivers call `fpga_bridge_register`. Region code collects bridge references by OF node or parent device and adds them to a list. Programming disables the list, loads the FPGA image, and enables the list. On post-remove or cleanup, `fpga_bridges_put` releases each bridge and removes it from the list under a spinlock.

State and persistence: global state is the bridge class, IDA, and `bridge_list_lock`. Per-bridge state includes name, ops, owner module, private pointer, mutex, list node, and transient `info` pointer. Hardware state is whatever the low-level `enable_set`, `enable_show`, or `fpga_bridge_remove` callbacks implement.

Dependencies and integration points: depends on the device class infrastructure, OF platform population, IDA, module refs, mutexes, spinlocks, and `<linux/fpga/fpga-bridge.h>`. It is consumed by `fpga-region.c` and `of-fpga-region.c` and by low-level bridge drivers outside this subset.

Risks and test signals: risks include list manipulation while bridge devices are being unregistered, bridge callbacks being optional, `info` being shared transiently with low-level drivers, and exclusive locking causing `-EBUSY` on overlapping reconfiguration. Test signals are `/sys/class/fpga_bridge/br*/name` and `state`, KUnit bridge tests, successful OF bridge acquisition, bridge disable/enable ordering during region programming, and clean put/unregister without module ref leaks.

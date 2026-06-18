# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar.h

## Purpose
Declares the small public interface for RPA Dynamic Logical Partitioning of I/O slots on PPC64 pSeries systems.

## Important APIs, Types, and Functions
The header declares `dlpar_sysfs_init()`, `dlpar_sysfs_exit()`, `dlpar_add_slot()`, and `dlpar_remove_slot()`. It has only an include guard and no local types.

## Control Flow
There is no executable flow. `rpadlpar_core.c` implements add/remove operations and calls the sysfs init/exit helpers implemented by `rpadlpar_sysfs.c`.

## State and Persistence Behavior
No state is stored here. The declarations define the module-internal boundary for sysfs-triggered DLPAR operations.

## Dependencies and Integration Points
Consumed by `rpadlpar_core.c` and `rpadlpar_sysfs.c`; indirectly integrates with RTAS, VIO, PCI PHB, and rpaphp slot operations.

## Risks
Signature drift breaks the sysfs-to-core call boundary. Since DLPAR operations are string-keyed by DRC name, callers must honor `MAX_DRC_NAME_LEN` from `rpaphp.h` even though this header does not restate it.

## Test Signals
Compile coverage of `rpadlpar_core.c` and `rpadlpar_sysfs.c`, module load on DLPAR-capable partitions, and sysfs add/remove slot calls validate the interface.

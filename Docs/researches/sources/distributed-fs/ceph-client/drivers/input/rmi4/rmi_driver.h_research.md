<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.h -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.h

## Purpose
`rmi_driver.h` is the internal header for the RMI4 physical driver and function handlers. It defines PDT constants, register descriptor structures, core helper prototypes, optional function helper stubs, and handler externs.

## Important APIs, Types, and Functions
Important definitions include `SYNAPTICS_INPUT_DEVICE_NAME`, `SYNAPTICS_VENDOR_ID`, `PDT_PROPERTIES_LOCATION`, `BSR_LOCATION`, `RMI_PDT_ENTRY_SIZE`, `PDT_START_SCAN_LOCATION`, `PDT_END_SCAN_LOCATION`, `struct pdt_entry`, `struct rmi_register_desc_item`, and `struct rmi_register_descriptor`. It declares PDT scanning, register descriptor parsing, IRQ probing, function initialization, sensor enabling, suspend/resume helper dependencies, F03 button helpers, F34 sysfs helpers, and all function handler externs.

## Control Flow
The header defines the shared contracts: `rmi_driver.c` scans PDT entries and creates function devices; function handlers use register descriptor helpers and optional F03/F34 helpers; `rmi_bus.c` registers the handler externs selected by Kconfig.

## State and Persistence
The register descriptor structures are allocated per function as needed and describe query/control/data packet layouts. PDT entries are transient scan results copied into function descriptors.

## Dependencies and Integration Points
It includes Linux input, timing, ctype, and `rmi_bus.h`. It is included by RMI core and function implementation files such as `rmi_f01.c` and `rmi_2d_sensor.c`.

## Risks and Edge Cases
Optional helper stubs return success when features are disabled, so callers must be clear whether a no-op is acceptable. Handler externs must match Makefile/Kconfig inclusion or builds will fail. Register descriptor spelling uses `presense`, which is harmless but easy to duplicate incorrectly.

## Test Signals
Build matrix coverage for all Kconfig combinations is important. Runtime coverage comes from function handlers using PDT addresses, register descriptors, F03/F34 helpers, and IRQ setup without mismatched struct assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_driver.h -->

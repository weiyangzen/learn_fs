<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_pdt.h -->
# sources/distributed-fs/ceph-client/include/linux/of_pdt.h

## Purpose
This header declares interfaces for building a Linux device tree by querying an Open Firmware PROM through platform-supplied callback operations.

## Important APIs, types, and functions
`struct of_pdt_ops` contains PROM access callbacks: `nextprop`, `getproplen`, `getproperty`, `getchild`, `getsibling`, and `pkg2path`. `prom_early_alloc()` provides early allocation, and `of_pdt_build_devicetree()` builds the in-memory tree from a root phandle plus operations table.

## Control flow
Architecture PROM code supplies callbacks. The builder walks children/siblings, enumerates properties, allocates device nodes/properties early, resolves paths, and constructs the Linux OF tree.

## State and persistence
State created by `of_pdt_build_devicetree()` persists as the live OF tree. The callbacks access firmware PROM state but the header itself stores no state.

## Dependencies and integration points
It depends on phandle definitions from OF headers, early allocation, and architecture PROM implementations, especially legacy Open Firmware systems.

## Risks and test signals
Risks include callback buffer length mistakes, property length mismatch, zero phandle termination errors, early allocation leaks, and incorrect full paths. Test PROM tree builds, empty property lists, long paths, missing children/siblings, and architecture boot on PDT-based OF systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_pdt.h -->

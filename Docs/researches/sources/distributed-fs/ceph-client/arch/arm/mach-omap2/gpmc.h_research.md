<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/gpmc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/gpmc.h

## Purpose
`gpmc.h` is a compatibility include for the OMAP2 General-Purpose Memory Controller. It intentionally redirects users to the shared `linux/omap-gpmc.h` interface and notes that new code should not include this mach header.

## Important APIs, Types, and Functions
It declares no local APIs. Its only technical content is `#include <linux/omap-gpmc.h>`.

## Control Flow
There is no runtime control flow. It affects preprocessing by exposing the shared GPMC declarations through a legacy include path.

## State and Persistence Behavior
No state is stored or persisted.

## Dependencies and Integration Points
The dependency is `linux/omap-gpmc.h`. Integration is with old mach-omap2 code or board files that still include `arch/arm/mach-omap2/gpmc.h`.

## Risks
Keeping the wrapper can hide legacy dependencies that should migrate to the shared header. Removing it breaks any remaining includes. No hardware risk exists in the wrapper itself.

## Test Signals
Compile all OMAP GPMC users after include cleanup. `rg "mach-omap2/gpmc.h|#include \"gpmc.h\""` should identify remaining legacy dependencies before removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/gpmc.h -->

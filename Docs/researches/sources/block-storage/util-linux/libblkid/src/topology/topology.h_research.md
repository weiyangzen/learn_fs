# File Research: sources/block-storage/util-linux/libblkid/src/topology/topology.h

## Scope

Declares internal topology setter APIs and Linux topology idinfo symbols.

## Behavior

- Exposes setters for alignment, minimum/optimal I/O size, physical sector size, DAX, and disk sequence.
- Declares ioctl, md, evms, sysfs, dm, and lvm topology probers under `__linux__`.

## Dependencies And Risks

- Internal header couples topology drivers to `topology.c` setter semantics.
- Non-Linux builds see no topology prober declarations.

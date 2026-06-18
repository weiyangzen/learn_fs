# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-read.h

## Purpose
Declares the AFR directory read-side FOP entry points exported to the AFR translator operation table.

## Important APIs, types, and functions
Exports `afr_opendir()`, `afr_releasedir()`, `afr_readdir()`, and `afr_readdirp()` with Gluster call-frame, xlator, fd, loc, size, offset, and xdata signatures. The header is a narrow contract; implementation details such as `afr_do_readdir()` and callbacks remain private to the `.c` file.

## Control flow
Translator initialization wires these prototypes into the fops table. Runtime calls enter the `.c` implementation, which creates frame-local AFR state and either broadcasts opens or routes reads through read-transaction selection.

## State and persistence behavior
The header declares no state. The implied state is fd context lifecycle: open/read operations maintain AFR fd context and `releasedir` releases it.

## Dependencies and integration points
Requires the broader AFR/Gluster type environment for `call_frame_t`, `xlator_t`, `loc_t`, `fd_t`, and `dict_t`. It is included by AFR registration and compile units needing directory read FOP prototypes.

## Risks and test signals
The main risk is signature drift against Gluster fop expectations or implementation definitions. Compile coverage and translator fop-table tests should catch mismatched prototypes; runtime tests should verify all declared entry points are registered.

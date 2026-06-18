# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/Makefile

## Purpose
This Kbuild makefile builds the EFA LNet Network Driver module `kefalnd.o` from its implementation files and exposes the EFA provider include path.

## Important APIs, Types, And Functions
`kefalnd-objs` includes `efalnd.o`, `efalnd_modparams.o`, `efalnd_peerni.o`, `efalnd_connection.o`, and `efalnd_debugfs.o`. `NOSTDINC_FLAGS += -I $(EFA_INCLUDE_PATH)` adds the EFA kernel verbs headers. `CONFIG_GCOV_PROFILE_LNET` enables `GCOV_PROFILE`.

## Control Flow
When the parent makefile includes `efalnd/`, Kbuild links the listed objects into `kefalnd.o`. The include path must resolve `efa_verbs.h` and related EFA-specific definitions during compilation.

## State, Persistence, And Dependencies
No runtime state exists. The build depends on `EFA_INCLUDE_PATH`, RDMA/EFA kernel headers, and the Lustre/LNet include tree.

## Integration Points
It is selected by `CONFIG_LNET_EFALND` in `lnet/klnds/Makefile` and produces the module that registers the `EFALND` LNet driver at init.

## Risks
Missing or incompatible `EFA_INCLUDE_PATH` breaks compilation. Omitting one object file can remove module parameters, peer metadata discovery, connection state handling, or debugfs support. GCOV profile support should remain conditional to avoid unwanted instrumentation.

## Test Signals
Build tests should compile EFALND with and without GCOV, validate that all object files link into `kefalnd.o`, and verify include path failures are caught early.

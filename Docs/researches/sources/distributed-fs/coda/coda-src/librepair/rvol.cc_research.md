# sources/distributed-fs/coda/coda-src/librepair/rvol.cc

Purpose: manages repair-time remounting of a conflict volume. `repair_mountrw` asks Venus to mount a mutable replica view, records the generated mount point, and updates conflict bookkeeping; `repair_finish` unmounts and cleans temporary repair state.

APIs and flow: the mount path uses conflict metadata, `ViceIoctl`, and repair pathname helpers to issue Coda pioctls. On success it records mount path/FID state in `struct conflict`; cleanup paths remove temporary directories and unwind pioctl state. It treats mount failures as user-visible repair errors through `msg`/`msgsize`.

State/dependencies: integrates with `repcmds` conflict structures, Venus ioctls, Coda path helpers, and volume/FID types. State is persisted outside this file in Venus/server repair state rather than local files. Risks include many early exits with partially initialized conflict fields, dependence on exact pioctl behavior, and cleanup requiring correct conflict state. Test signals are repair command workflows rather than local tests.

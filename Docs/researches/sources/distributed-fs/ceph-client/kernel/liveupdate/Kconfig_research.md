# sources/distributed-fs/ceph-client/kernel/liveupdate/Kconfig

## Purpose
`Kconfig` defines the configuration menu for Kexec Handover and the Live Update Orchestrator. It ties live update support to architecture kexec handover capability, KHO scratch memory, file-based kexec, libfdt, CMA, debug options, and optional memfd preservation.

## Important APIs, Types, and Functions
Configuration symbols are `KEXEC_HANDOVER`, `KEXEC_HANDOVER_DEBUG`, `KEXEC_HANDOVER_DEBUGFS`, `KEXEC_HANDOVER_ENABLE_DEFAULT`, `LIVEUPDATE`, and `LIVEUPDATE_MEMFD`. `KEXEC_HANDOVER` selects `MEMBLOCK_KHO_SCRATCH`, `KEXEC_FILE`, `LIBFDT`, and `CMA`; `LIVEUPDATE` depends on `KEXEC_HANDOVER`; `LIVEUPDATE_MEMFD` depends on memfd and shmem support.

## Control Flow
Build-time selection controls which source files compile and which command-line defaults apply. `KEXEC_HANDOVER_ENABLE_DEFAULT` initializes KHO as enabled unless `kho=off` is passed. `LIVEUPDATE` enables the `/dev/liveupdate` orchestrator and KHO subtree management.

## State and Persistence Behavior
The file has no runtime state. Its choices determine whether handover metadata, scratch reservations, debugfs, and liveupdate state persistence are available.

## Dependencies and Integration Points
It integrates with architecture KHO support, kexec file loading, FDT metadata, CMA/memblock scratch handling, debugfs, and memfd/shmem liveupdate support.

## Risks and Test Signals
Configuration dependency mistakes can produce builds without required memblock/libfdt/CMA support or expose LUO without KHO. Test signals include `allmodconfig`/`allyesconfig` builds, KHO disabled by command line despite default enable, debugfs on/off builds, and LIVEUPDATE_MEMFD dependency builds.

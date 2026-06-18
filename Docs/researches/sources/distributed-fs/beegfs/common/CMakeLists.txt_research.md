<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/CMakeLists.txt -->
## sources/distributed-fs/beegfs/common/CMakeLists.txt

### Purpose
This CMake file defines the BeeGFS common userspace build. It collects a large static `beegfs-common` library, the `test-common` executable, and the dynamically loaded `beegfs_ib` RDMA socket library.

### Important APIs, Types, And Functions
The build requires `pkg-config` and `libnl-route-3.0`, adds `source` as an include root, and links `beegfs-common` with libnl, OpenSSL, and crypto. The optional test target includes focused unit tests for networking, path, locking, serialization, bit stores, striping, and `TimerQueue`. The `beegfs_ib` target contains `RDMASocketImpl`, `IBVSocket`, and `OpenTk_IBVSocket`.

### Control Flow
Configuration first resolves libnl, then declares `beegfs-common` with all common source/header inputs. Tests are added unless `BEEGFS_SKIP_TESTS` is set. The RDMA library is declared after common code and linked with `rdmacm` and `ibverbs`.

### State, Persistence, And Dependencies
This file persists build graph membership rather than runtime state. It is the integration point that decides whether common code, tests, and RDMA support compile and how they link to system libraries.

### Integration Points
All services and tools using BeeGFS common code depend on this target. `beegfs_ib` installs to `usr/lib` as component `libbeegfs-ib`, matching the runtime RDMA socket callback/plugin path.

### Risks
The static source list is easy to desynchronize from repository changes. RDMA builds require system `rdmacm`/`ibverbs`; missing development packages break `beegfs_ib`. Tests only cover a subset of common components, so build success does not validate all listed networking and config paths.

### Test Signals
Run the CMake configuration, build `beegfs-common` and `beegfs_ib`, and run `ctest` for `test-common`. `TestTimerQueue.cpp` is the direct signal for the timer component in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/CMakeLists.txt -->

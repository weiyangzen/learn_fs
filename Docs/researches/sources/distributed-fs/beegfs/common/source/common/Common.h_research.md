<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/Common.h -->
## sources/distributed-fs/beegfs/common/source/common/Common.h

### Purpose
`Common.h` is a broad compatibility and utility header shared across BeeGFS common code. It centralizes includes, typedefs, timeout defaults, memory macros, compiler compatibility shims, logging type definitions, debug assertions, and data-version constants.

### Important APIs, Types, And Functions
It defines container typedefs for string and integer maps/lists/vectors/sets, `CONN_LONG_TIMEOUT`, `CONN_MEDIUM_TIMEOUT`, `CONN_SHORT_TIMEOUT`, `BEEGFS_MIN/MAX`, `SAFE_DELETE`, `SAFE_FREE`, `SAFE_ASSIGN`, `likely/unlikely`, `BEEGFS_BUG_ON`, `LogType`, compiler shims for `override`, enum class equality, `nullptr`, `noexcept`, `std::chrono::steady_clock`, `ASSERT`, `USE_READDIR_R`, `BEEGFS_FALLTHROUGH`, `BEEGFS_NODISCARD`, and `BEEGFS_DATA_VERSION`.

### Control Flow
Most content is compile-time. Runtime behavior appears in macros that free memory, log bugs/backtraces, or invoke debug assertions.

### State, Persistence, And Dependencies
The file introduces no owned state, but its constants affect network timeouts and protocol/data version compatibility. It depends on many libc, POSIX, STL, networking, pthread, and Boost headers.

### Integration Points
Almost every file in this subset includes `Common.h` directly or indirectly. Config defaults use the connection timeout constants, logging uses `LogType`, RDMA and listeners use `likely/unlikely` and safe free macros.

### Risks
Because this header is global, changes have very large blast radius. Macros evaluate arguments in conventional macro ways and can hide ownership changes. The compatibility shims for old compilers may be obsolete but still affect parsing.

### Test Signals
Build coverage is the main signal. Focused checks should cover debug assertion behavior, timeout defaults via config fallback, `BEEGFS_DATA_VERSION` compatibility, and macro use in cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/Common.h -->

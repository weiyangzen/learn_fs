<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.cpp

### Purpose
`RDMASocket.cpp` dynamically loads the BeeGFS RDMA socket implementation from `libbeegfs_ib.so` and exposes availability, device detection, fork initialization, and socket creation through callback pointers.

### Important APIs, Types, And Functions
An internal `IBLibLoader` calls `dlopen("libbeegfs_ib.so", RTLD_NOW)` at startup and looks up `beegfs_socket_impl` with `dlsym()`. Public methods `isRDMAAvailable()`, `rdmaDevicesExist()`, `rdmaForkInitOnce()`, and `create()` delegate to loaded callbacks.

### Control Flow
If the shared library cannot load or lacks the callback symbol, RDMA remains unavailable. `create()` throws `std::logic_error` when called without a loaded implementation.

### State, Persistence, And Dependencies
The static loader owns the dynamic-library handle until process exit. Dependencies include `dlfcn.h` and the ABI contract of `RDMASocket::ImplCallbacks`.

### Integration Points
NIC discovery probes RDMA availability through this file, and connection pools create RDMA sockets through the callback interface.

### Risks
ABI mismatch in `beegfs_socket_impl` can crash at callback use. Startup-time loading means environment/library path issues decide RDMA support globally. Tests should cover missing library, missing symbol, callback success, create-without-support exception, and device-detection false/true cases using a test shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.cpp -->

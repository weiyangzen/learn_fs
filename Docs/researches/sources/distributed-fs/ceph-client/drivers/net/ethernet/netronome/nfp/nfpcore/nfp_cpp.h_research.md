# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cpp.h

Purpose: Main public/internal interface for low-level NFP CPP bus access. It defines CPP ID packing, interface IDs, area APIs, raw read/write helpers, mutex APIs, explicit transaction APIs, and the backend operation table.

Important APIs/types/functions: Macros `NFP_CPP_ID()`, `NFP_CPP_ISLAND_ID()`, `NFP_CPP_ID_*_of()`, `NFP_CPP_INTERFACE()`, and interface extractors define addressing. `struct nfp_cpp_operations` is the transport vtable. Area APIs include `nfp_cpp_area_alloc*()`, acquire/release, read/write, iomem/resource access, and scalar helpers. Other groups cover XPB access, CPP mutexes, explicit transactions, model detection, and `nfp_cpp_map_area()`.

Control flow/state: The header describes object lifetimes owned by `nfp_cppcore.c`: a CPP handle owns transport state, areas must be acquired before access, explicit handles are acquired/released per transaction sequence, and mutexes represent hardware MU atomic locks.

Dependencies/integration: Included by nearly every nfpcore and NFP NIC file. Backends such as `nfp6000_pcie.c` implement `struct nfp_cpp_operations`; higher layers such as resources, NSP, runtime symbols, and DCB build on these APIs.

Risks: CPP ID and interface packing are contract-critical. The area API allows direct device access, so misuse of alignment, width, or acquire/release ordering can produce hardware faults or BAR leaks. Logging macros assume `nfp_cpp_device(cpp)->parent` is valid.

Test signals: Compile all NFP modules, run probe/unload, exercise scalar and bulk CPP reads/writes, XPB read-modify-write, mutex locking, explicit read/write, and area mapping consumers.

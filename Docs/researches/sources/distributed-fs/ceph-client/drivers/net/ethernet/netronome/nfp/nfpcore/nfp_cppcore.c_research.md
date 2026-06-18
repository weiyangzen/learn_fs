# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cppcore.c

Purpose: Implements the generic CPP bus object, area lifetime, resource bookkeeping, hot area cache, XPB helpers, model/interface discovery, and explicit transaction wrapper methods.

Important APIs/types/functions: `struct nfp_cpp` embeds a Linux device and owns model/interface/serial, IMB CAT table, resource list, waitqueue, and area cache. `struct nfp_cpp_area` tracks a mapped CPP region and private backend data. `nfp_cpp_from_operations()` constructs the bus from backend ops. `nfp_cpp_area_alloc*()`, `nfp_cpp_area_acquire*()`, `nfp_cpp_area_release*()`, `nfp_cpp_read/write()`, and scalar helpers are core access paths. `area_cache_get/put()` implements LRU cached windows. `nfp_xpb_*()` converts XPB addressing to CPP. `nfp_cpp_explicit_*()` wraps backend explicit operations.

Control flow: Construction initializes locks/lists/device, calls backend init, autodetects model, reads IMB mapping via XPB, and computes MU locality. Normal reads/writes split requests at `NFP_CPP_SAFE_AREA_SIZE` boundaries, use cached acquired areas where possible, otherwise allocate/acquire/release short-lived areas. Area acquisition increments a logical refcount and waits until backend resources are available; final release wakes waiters.

State and persistence: State is in-memory: resource list, area krefs/refcounts, cached area list, IMB table, and embedded device registration. Device state is accessed through backend ops but not persisted by this file.

Dependencies/integration: Depends on `nfp_cpp_operations` backend implementations, target translation from `nfp_target_cpp()`, scalar helpers from `nfp_cpplib.c`, ARM register constants, and Linux device/kref/waitqueue primitives. All nfpcore higher layers use these functions.

Risks: Resource cleanup is delicate; dangling areas are logged and force-cleaned during `nfp_cpp_free()`. Area cache reinitialization must not leak acquired backend windows. Pointer arithmetic on `void *` buffers and copied-source duplicate lines in this snapshot should be compile-checked. XPB island conversion is hardware-specific.

Test signals: Probe should log model, serial, and interface. Stress repeated CPP reads/writes across safe-window boundaries, cached and uncached areas, nonblocking acquire, unload with no dangling area warnings, and XPB read/write on ARM/non-ARM interfaces.

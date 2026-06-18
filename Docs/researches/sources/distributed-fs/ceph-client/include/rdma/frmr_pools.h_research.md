# sources/distributed-fs/ceph-client/include/rdma/frmr_pools.h

Purpose: declares a device-level fast-registration memory-region pool interface for RDMA devices. It lets provider drivers create/destroy batches of FRMR handles and lets core/users push or pop pool-backed memory regions.

Important APIs and types: `struct ib_frmr_key` describes pool keys with vendor key, optional kernel-only vendor key, DMA block count, access flags, and ATS flag. `struct ib_frmr_pool_ops` supplies provider callbacks `create_frmrs()`, `destroy_frmrs()`, and `build_key()`. Public functions are `ib_frmr_pools_init()`, `ib_frmr_pools_cleanup()`, `ib_frmr_pool_pop()`, and `ib_frmr_pool_push()`.

Control flow: an RDMA provider initializes pools on `ib_device` registration with pool ops, creates batches of FRMR handles for matching keys, hands an available handle to an `ib_mr` on pop, and returns it on push. Cleanup destroys remaining handles through provider ops.

State and persistence: pool state is associated with the `ib_device` and individual `ib_mr` objects at runtime. `kernel_vendor_key` distinguishes kernel-only pools from general pools. Nothing persists beyond device lifetime.

Dependencies and integration points: depends on `ib_device`, `ib_mr`, page sizing, provider MR allocation/destruction, and access flag conventions from verbs. It integrates memory registration acceleration with device-specific handle allocation.

Risks and test signals: risks include key mismatches causing MR reuse with wrong access or DMA geometry, pool leaks on device teardown, kernel-only pool exposure, ATS flag misinterpretation, and pop/push imbalance. Test provider init/cleanup, handle batch creation failure unwind, repeated MR allocation/free, access-flag variants, ATS on/off, and device removal with outstanding MRs.

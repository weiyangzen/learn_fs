# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nffw.c

Purpose: Reads the `nfp.nffw` firmware-info resource and finds the MIP address for loaded firmware.

Important APIs/types/functions: Versioned firmware info layouts `nfp_nffw_info_v1/v2`, `struct nffw_fwinfo`, and `struct nfp_nffw_info` model the resource. Public APIs are `nfp_nffw_info_open()`, `_close()`, and `nfp_nffw_info_mip_first()`.

Control flow: Open allocates state, acquires the `NFP_RESOURCE_NFP_NFFW` lock, reads the whole known structure, verifies initialized flag and supported version, then keeps the resource locked until close. MIP lookup chooses the first loaded firmware info entry and returns CPP ID and offset, forcing MU direct access bits when the firmware entry marks MU direct addressing.

State and persistence: Kernel state is a locked resource handle plus copied firmware info. Persistent state lives in the device resource table and firmware-managed NFFW resource.

Dependencies/integration: Uses `nfp_resource_acquire()`, CPP reads, NFP6000 MU locality helpers, and is consumed by `nfp_mip.c`.

Risks: Unsupported future NFFW versions fail open. The file reads `sizeof(*fwinf)` and requires resource size to cover it, which may reject smaller valid future/variant layouts. Only the first loaded firmware is surfaced.

Test signals: Test NFFW v1/v2 initialized resources, uninitialized/future-version failure, loaded-entry selection, MU direct-address adjustment, and lock release on all exits.

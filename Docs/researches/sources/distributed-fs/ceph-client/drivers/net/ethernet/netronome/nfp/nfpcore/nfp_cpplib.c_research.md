# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_cpplib.c

Purpose: Provides convenience CPP access helpers above `nfp_cpp_read/write()`: little-endian scalar reads/writes, model autodetection, explicit read/write chunking, and area mapping.

Important APIs/types/functions: `nfp_cpp_readl/writel/readq/writeq()` marshal little-endian scalar values. `nfp_cpp_model_autodetect()` reads XPB PL device ID and adjusts NFP6000-family model IDs. `nfp_cpp_explicit_read/write()` acquire an explicit handle, set target/posting, transfer up to 128-byte chunks, and release. `nfp_cpp_map_area()` allocates and acquires a CPP area and returns iomem.

Control flow/state: Scalar helpers perform one bulk CPP transaction and translate short transfers to `-EIO`. Explicit helpers validate length alignment, translate `NFP_CPP_ACTION_RW` to read or write action, calculate byte masks, loop over chunks, and unwind the explicit handle on failure. No persistent state is owned here.

Dependencies/integration: Depends on `nfp_cppcore.c` APIs, explicit backend ops, NFP6000 XPB register constants, Linux unaligned and bitfield helpers. Used throughout resource, NSP, runtime symbol, and NIC code.

Risks: Explicit byte masks are address/width-sensitive; wrong masks can corrupt adjacent bytes. Explicit acquisition can fail under slot pressure. `nfp_cpp_map_area()` returns `ERR_PTR(-EIO)` for several allocation/mapping failures, losing some detail.

Test signals: Validate scalar endian behavior, explicit unaligned read/write fallback from PCIe area code, model autodetect on NFP3800 and NFP6000-family IDs, and map/unmap through `nfp_cpp_area_release_free()`.

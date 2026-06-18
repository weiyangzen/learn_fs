<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.h

## Purpose

`spectrum_acl_tcam.h` declares the shared TCAM data structures and APIs used by the Spectrum ACL core, TCAM virtualization layer, C-TCAM backend, A-TCAM backend, ERP manager, and Bloom filter. It is the internal contract that lets chip-specific TCAM operations plug into generic ruleset/rule handling.

## Important APIs, Types, And Functions

- `struct mlxsw_sp_acl_tcam` is the top-level TCAM allocator state embedded in `struct mlxsw_sp_acl`.
- `struct mlxsw_sp_acl_profile_ops` defines high-level ruleset/rule callbacks consumed by `spectrum_acl.c`.
- `struct mlxsw_sp_acl_tcam_region` carries hardware region id, key type, region info payload, key-info, group/vregion linkage, and backend-private storage.
- C-TCAM structs and functions expose region/chunk/entry lifecycle, entry add/delete, action replacement, and entry offset.
- A-TCAM structs and functions expose region/chunk/entry lifecycle, entry add/delete/action replacement, rehash hints, and container conversions.
- ERP declarations expose mask references, delta helpers, Bloom insertion/removal, region lifecycle, rehash hints, and global ERP init/fini.
- Bloom declarations expose per-entry add/delete and global Bloom init/fini.

## Control Flow

The header has no runtime control flow, but it defines the call graph. High-level ACL code obtains profile ops from `mlxsw_sp_acl_tcam_profile_ops()`. Profile ops call TCAM virtual entry helpers. The virtual layer calls chip backend ops, which use C-TCAM or A-TCAM structures. A-TCAM calls ERP and Bloom helpers declared here. Inline conversion helpers recover A-TCAM containers from embedded C-TCAM objects.

## State And Persistence

The header defines all main in-memory state carriers for TCAM ACLs and their backend-private flexible arrays. Hardware-persistent state represented by these structs includes ACL region IDs, TCAM region info, group IDs, entries, ERP masks/tables, and Bloom bits. No state is stored by the header itself.

## Dependencies And Integration Points

It depends on Linux list, `parman`, IDR/IDA-related use, Spectrum core headers, register constants, and AFK definitions. It is included by `spectrum_acl.c`, `spectrum_acl_tcam.c`, `spectrum_acl_ctcam.c`, `spectrum_acl_atcam.c`, `spectrum_acl_erp.c`, `spectrum_acl_bloom_filter.c`, and multicast TCAM code.

## Risks

- Flexible-array private storage requires allocation sizes from the matching ops; a mismatch corrupts backend state.
- Shared structs encode ownership assumptions that are not enforced by the type system, especially embedded C-TCAM inside A-TCAM.
- Constants such as mask length, base region count, resize step, and catchall priority are hardware-policy contracts.
- Header changes can ripple across all ACL backends and profiles.

## Test Signals

Compile coverage across all Spectrum variants, backend init/fini, C-TCAM and A-TCAM entry lifecycle tests, ERP/Bloom integration, action replacement, rehash, and static analysis for container/flexible-array usage provide the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_tcam.h -->

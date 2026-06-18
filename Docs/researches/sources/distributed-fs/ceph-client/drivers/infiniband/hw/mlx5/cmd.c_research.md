# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cmd.c

## Purpose
This file provides mlx5 IB-facing wrappers for common mlx5 firmware commands. It keeps command input/output packing local to the driver and exposes concise helpers for special mkeys, congestion query, transport objects, multicast groups, XRC domains, MAD IFC, UARs, and VUID query.

## Important APIs, types, and functions
Functions exported through `cmd.h` include `mlx5r_cmd_query_special_mkeys`, `mlx5_cmd_query_cong_params`, `mlx5_cmd_destroy_tir`, `mlx5_cmd_destroy_tis`, `mlx5_cmd_destroy_rqt`, `mlx5_cmd_alloc_transport_domain`, `mlx5_cmd_dealloc_transport_domain`, `mlx5_cmd_dealloc_pd`, `mlx5_cmd_attach_mcg`, `mlx5_cmd_detach_mcg`, `mlx5_cmd_xrcd_alloc`, `mlx5_cmd_xrcd_dealloc`, `mlx5_cmd_mad_ifc`, `mlx5_cmd_uar_alloc`, `mlx5_cmd_uar_dealloc`, and `mlx5_cmd_query_vuid`.

## Control flow
Each wrapper builds a firmware input mailbox with `MLX5_SET`, sets opcode and identifiers, calls the appropriate `mlx5_cmd_exec*` helper, and extracts output fields with `MLX5_GET` when needed. Allocation helpers return ids only after successful commands. Destroy/dealloc helpers mostly ignore returned firmware status when declared `void`. `mlx5_cmd_mad_ifc` allocates dynamic input/output buffers, handles SMI device port-plane translation, copies the MAD request into the command buffer, executes, and copies the response MAD back out. `mlx5r_cmd_query_special_mkeys` first checks capabilities and then fills cached null, dump-fill, and terminate-scatter-list mkeys.

## State and persistence behavior
State changes happen in firmware and in the driver's in-memory caches. Allocated TDNs, XRCDs, UARs, MCG attachments, and special mkeys persist only while the device context and firmware resources exist. There is no file persistence.

## Dependencies and integration points
The file depends on `mlx5_ib.h`, `cmd.h`, mlx5 command layout macros, core command execution, SMI native-port translation, multicast GID data, and RDMA MAD/XRC/UAR consumers in other mlx5 IB files.

## Risks
Risks include opcode/field mismatches, endian mistakes for cached mkeys, silent failures in `void` destroy helpers, incorrect SMI port translation, memory allocation failure paths in MAD IFC, and callers forgetting to pair allocations and deallocations. VUID query uses a stack buffer sized for a large variable field and must remain aligned with firmware layout definitions.

## Test signals
Firmware command selftests or fault injection should verify allocation/deallocation pairing, MCG attach/detach, MAD IFC on normal and SMI devices, special mkey capability combinations, UAR allocation failure cleanup, XRC domain lifecycle, and VUID query output sizing.

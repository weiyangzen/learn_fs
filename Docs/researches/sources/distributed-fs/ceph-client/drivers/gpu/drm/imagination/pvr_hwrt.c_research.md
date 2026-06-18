# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_hwrt.c

## Purpose
Implements hardware render target dataset creation and teardown. It validates freelist dependencies, computes render target/tile/MSAA hardware register values, creates common and per-RT firmware structures, allocates optional render-target arrays, and links HWRT data to free lists for reconstruction.

## Important APIs, types, and functions
- `pvr_hwrt_dataset_create()` creates a dataset with two RT data structures and common FW state.
- `pvr_destroy_hwrt_datasets_for_file()` and `pvr_hwrt_dataset_put()` manage lifetime.
- Internal initialization helpers include `hwrt_init_kernel_structure()`, `hwrt_init_common_fw_structure()`, and `hwrt_data_init_fw_structure()`.
- Register-value helpers include `get_cr_isp_mtile_size_val()`, `get_cr_multisamplectl_val()`, and `get_cr_te_aa_val()`.
- `struct pvr_rt_mtile_info` stores derived macrotile geometry used to fill common HWRT data.

## Control flow
Creation allocates a dataset, looks up all required freelists from file handles, rejects local freelists below `pvr_get_free_list_min_pages()`, computes tile counts from render dimensions and feature tile size, chooses macrotile layout based on `simple_parameter_format_version`, fills common HWRT register values and merge/MSAA/region-header fields, then creates a FW object initialized from the common struct.

For each of the two RT data slots, it records FW addresses for the common object and freelists, stores userspace-supplied device addresses for tail pointers, vheap table, RTC, PM mlist, macrotile array, and region headers, initializes RTA control, optionally allocates SRTC and RAA FW objects for multi-layer render targets, creates the per-RT HWRT FW object, and links the HWRT data to the local freelist. Release sends FW cleanup for each HWRT data object before destroying per-slot and common FW objects and dropping freelist refs.

## State and persistence
`struct pvr_hwrt_dataset` persists under a file handle with a kref, two `pvr_hwrt_data` entries, freelist references, common FW object, and `max_rts`. Each `pvr_hwrt_data` has a local copy of firmware state, a FW object, optional SRTC/RAA objects, and a freelist node. Firmware sees both common and per-RT structures until cleanup and destruction.

## Dependencies and integration points
Depends on freelist lookup/refcounting, common FW object helpers, Rogue FWIF render structures, Rogue CR bitfield definitions, PVR feature values for tile and sample layout, and xarray handle storage. Jobs reference `pvr_hwrt_data` for geometry/fragment submissions, and free-list reconstruction resets linked HWRT state.

## Risks
The code trusts many UAPI-provided GPU device addresses and sizes after basic setup; validation likely occurs in stream/UAPI layers. Feature-derived MSAA/tile bitfields are hardware-sensitive. Cleanup warnings during release indicate firmware still owns HWRT state. Partial initialization must unwind optional SRTC/RAA and freelist links correctly.

## Test signals
Validate dataset creation for single-layer and multi-layer render targets, all supported sample counts, simple and non-simple parameter formats, local freelist minimum enforcement, bad freelist handles, cleanup on partial failures, FW cleanup warnings, and geometry/fragment jobs using both RT data slots.

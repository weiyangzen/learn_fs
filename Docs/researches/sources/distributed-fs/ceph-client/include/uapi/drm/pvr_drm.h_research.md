# sources/distributed-fs/ceph-client/include/uapi/drm/pvr_drm.h

## Purpose
This header is the public userspace/kernel ABI for the Imagination PowerVR DRM driver. It defines ioctl numbers, fixed-layout argument records, query records, object-array versioning, GPU virtual-memory controls, render context setup, PM/free-list setup, HWRT dataset setup, and syncobj-backed job submission. It is not executable code, but it is a persistent ABI: field ordering, numeric ioctl IDs, enum values, padding requirements, and reserved-bit handling are part of the contract with Mesa/userspace.

## Important APIs and types
The `PVR_IOCTL()` macro maps driver ioctl IDs `0x00` through `0x0d` to `DRM_IOCTL_PVR_*` commands. The lifecycle is built around `DRM_IOCTL_PVR_DEV_QUERY`, `CREATE_BO`, `GET_BO_MMAP_OFFSET`, `CREATE_VM_CONTEXT`, `VM_MAP`, `CREATE_CONTEXT`, `CREATE_FREE_LIST`, `CREATE_HWRT_DATASET`, and `SUBMIT_JOBS`, with matching destroy/unmap calls.

`struct drm_pvr_obj_array` is the important extensibility primitive. It carries `stride`, `count`, and a userspace array pointer so indirect arrays can be versioned the same way ioctl structs are. Query records include GPU BVNC identity, runtime limits, quirks, enhancements, heap information, and static data areas. BO flags cover device-cache bypass, PM/firmware protection, and CPU userspace mapping. VM map/unmap structs bind GEM handles into userspace-managed GPU VA heaps. Context enums distinguish render, compute, and transfer-fragment contexts with low/normal/high priorities. `drm_pvr_sync_op`, `drm_pvr_job`, and `drm_pvr_ioctl_submit_jobs_args` define job submission with binary or timeline syncobj wait/signal operations.

## Control flow and state
Userspace first queries device/runtime data, especially heaps and static data areas. It then creates GEM BOs, asks for mmap offsets if CPU access is permitted, creates a VM context, and maps BO ranges into one of the advertised heaps. Render-capable workloads create typed contexts, PM protected free lists, and HWRT datasets. `SUBMIT_JOBS` passes an array of typed jobs, each with a command stream pointer, sync operation array, compatible context handle, flags, and optional HWRT reference. On submission error, `jobs.count` is repurposed as the failing job index, which is an ABI-visible control-flow signal.

## State and persistence behavior
Handles returned by create ioctls are per-DRM-file kernel objects and remain valid until explicit destroy/close or file teardown. GPU virtual mappings persist in the VM context until unmapped. HWRT datasets reference previously created free lists and GPU addresses, so stale handles or address-space reuse can corrupt later submissions. Query values are runtime/device facts and may vary by GPU generation. Padding and implicit union padding are required to be zero, giving the kernel deterministic ABI validation and room for forward-compatible expansion.

## Dependencies and integration points
The header depends on `drm.h`, `linux/types.h`, and `linux/const.h`. It integrates with DRM GEM handles, real `mmap()` on DRM fake offsets, DRM syncobj/timeline syncobj semantics, UMD command stream generation, and PowerVR firmware/runtime heap layouts. Userspace must coordinate with kernel heap information rather than invent GPU virtual addresses outside advertised regions.

## Risks and test signals
Main risks are ABI breakage from reordering append-only enums, changing struct layout, ignoring MBZ padding, accepting reserved flag bits, or failing 32/64-bit pointer compatibility. Security-sensitive paths include userspace pointers, command streams, BO/VM mapping ranges, and PM/firmware-protected BO flags. Test signals should include ioctl struct size/alignment checks, zero-padding rejection, invalid flag rejection, heap-boundary mapping failures, destroy-after-use behavior, syncobj wait/signal paths, timeline values, failed multi-job index reporting, and 32-bit compat tests.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_hwrt.h

## Purpose
Defines hardware render target data structures and lookup/lifetime APIs used by render submissions and file teardown.

## Important APIs, types, and functions
- `struct pvr_hwrt_data` stores one per-RT FW object, local firmware data copy, freelist linkage node, optional SRTC/RAA objects, and back pointer to its dataset.
- `struct pvr_hwrt_dataset` stores refcount, device pointer, common FW object/data, the fixed RT data array, referenced free lists, and maximum render targets.
- `pvr_hwrt_dataset_create()`, `pvr_destroy_hwrt_datasets_for_file()`, and `pvr_hwrt_dataset_put()` provide lifecycle APIs.
- Inline `pvr_hwrt_dataset_lookup()`, `pvr_hwrt_data_lookup()`, `pvr_hwrt_data_put()`, and `pvr_hwrt_data_get()` manage handle lookup and refcounts.

## Control flow
Dataset lookup locks the file xarray, loads a dataset handle, and takes a reference. RT data lookup first acquires the dataset, verifies the requested index is within the two-element data array, and returns the embedded data pointer while the dataset reference keeps it alive.

## State and persistence
The dataset owns both common and per-RT firmware state and freelist references. Per-RT data pointers are not independently refcounted; they borrow the dataset refcount and must be released with `pvr_hwrt_data_put()`.

## Dependencies and integration points
Depends on `pvr_device`, Rogue FWIF shared structs, UAPI HWRT creation args, xarrays, krefs, and freelist/FW object forward declarations. Jobs use HWRT data for geometry/fragment commands and reservation dependencies.

## Risks
Embedded per-RT data lifetime depends on correct dataset refcount handling. Future code must not store a `pvr_hwrt_data *` without holding the dataset reference. The fixed array sizes are tied to Rogue FWIF constants asserted in the implementation.

## Test signals
Build coverage for FWIF constant changes, handle lookup tests, out-of-range RT data index rejection, and job submission lifetime tests while datasets are concurrently destroyed are useful signals.

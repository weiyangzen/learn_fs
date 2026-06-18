# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_trace.h

## Purpose
Defines firmware trace state structures and declares firmware trace lifecycle/debugfs APIs.

## Important APIs, types, and functions
- `struct pvr_fw_trace_buffer` stores a FW buffer object, CPU mapping, and pointer to the firmware control entry for one thread.
- `struct pvr_fw_trace` stores the control object/mapping, per-thread buffers, and enabled trace group mask.
- Declares `pvr_fw_trace_init()`, `pvr_fw_trace_fini()`, and `pvr_fw_trace_debugfs_init()`.

## Control flow
No executable flow exists in the header. It defines the state consumed by common firmware initialization and debugfs setup.

## State and persistence
The structures represent persistent trace state owned by `pvr_fw_device`. Buffers are firmware-visible allocations and, in the implementation, are marked no-clear-on-reset.

## Dependencies and integration points
Depends on DRM file definitions, Linux types, and Rogue FWIF trace structs. The header is included by `pvr_fw.h`, `pvr_fw.c`, and the trace implementation.

## Risks
The array size is `ROGUE_FW_THREAD_MAX`; firmware/control structure thread-count mismatches are guarded in implementation by build checks. Adding trace groups or changing FWIF trace structures must keep these wrappers in sync.

## Test signals
Compile-time structure compatibility and runtime debugfs trace output are the main signals. Initialization must allocate one buffer per firmware thread.

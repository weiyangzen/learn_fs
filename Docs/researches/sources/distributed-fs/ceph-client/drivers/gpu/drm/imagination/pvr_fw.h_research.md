# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw.h

## Purpose
Defines the common firmware object, processor abstraction, firmware memory inventory, device firmware state, processor-type enum, and public firmware APIs shared by the PowerVR DRM driver.

## Important APIs, types, and functions
- `struct pvr_fw_object` wraps a GEM object mapped into firmware address space, its `drm_mm_node`, FW address offset, reset init callback, and list node.
- `struct pvr_fw_defs` is the processor vtable for init/fini, image processing, VM map/unmap, FW address conversion, wrapper init, IRQ check/clear, and fixed-data-address policy.
- `struct pvr_fw_mem` enumerates code/data/core sections plus FWIF objects such as connection control, OSINIT, SYSINIT, trace, power sync, fault page, runtime config, and MMU-cache sync.
- `struct pvr_fw_device` stores firmware metadata, boot state, processor data, heap geometry, address allocator, mapped FWIF pointers, trace state, and tracked FW-object list.
- Public APIs cover validation/init/fini, boot wait, hard reset, MTS kick, heap info calculation, layout lookup, MMU segment lookup, FW structure cleanup, FW object creation/mapping/destruction, address queries, and ELF command-stream processing.

## Control flow
The header mostly declares call surfaces. Inline wrappers delegate FW object CPU mapping to GEM vmap/vunmap, DMA lookup to GEM DMA address lookup, default FW address lookup to offset 0, and object-size lookup to the backing GEM size.

## State and persistence
It defines the driver-wide firmware persistence model: parsed firmware metadata, code/data shadows, FWIF shared structures, processor-specific data, mapped objects, and reset callbacks. `PVR_BO_FW_NO_CLEAR_ON_RESET` in the backing GEM flags controls whether an object survives hard reset without zero/init.

## Dependencies and integration points
Includes firmware info, trace, GEM, and DRM MM definitions. Processor definitions are provided externally by architecture files. Most driver subsystems depend on these helpers for firmware-visible allocations and addresses, including CCBs, contexts, HWRT, free lists, MMU cache commands, and trace.

## Risks
The vtable is mandatory for most operations; a missing or wrong processor callback breaks boot or address encoding. Many structures are shared with firmware ABI headers, so layout drift is high impact. Inline unmap-and-destroy assumes the object is currently CPU mapped.

## Test signals
Build coverage catches ABI signature drift. Runtime signals include firmware boot success, correct per-processor address encodings, successful creation/destruction of FW objects, and hard reset preserving only no-clear objects.

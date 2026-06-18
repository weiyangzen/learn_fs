# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_meta.h

## Purpose
Declares the small public META helper surface needed outside the META backend.

## Important APIs, types, and functions
- Forward declares `struct pvr_device`.
- Declares `pvr_meta_cr_read32(struct pvr_device *pvr_dev, u32 reg_addr, u32 *reg_value_out)`.

## Control flow
No runtime control flow is present. The declared function is implemented in `pvr_fw_meta.c` and used by firmware stop code for META-specific halt/debugger state inspection.

## State and persistence
No state is stored here. State accessed by the declared function is hardware slave-port register state.

## Dependencies and integration points
Depends only on Linux integer types and `pvr_device` forward declaration. Included by META implementation and start/stop code.

## Risks
The header intentionally exposes only a low-level register read helper. Broader META internals should remain private to avoid coupling generic firmware stop/start paths to META boot implementation details.

## Test signals
Build coverage catches declaration drift. Runtime signal is successful `pvr_fw_stop()` behavior on META firmware, including timeout propagation from slave-port polling.

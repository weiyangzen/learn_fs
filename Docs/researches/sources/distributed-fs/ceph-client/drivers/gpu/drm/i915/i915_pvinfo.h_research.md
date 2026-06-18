# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pvinfo.h

## Purpose

`i915_pvinfo.h` defines the paravirtualized vGPU shared-info page layout used between an i915 guest driver and a host emulator/GVT device model. It assigns the MMIO page offset, magic/version values, guest-to-host notification IDs, capability bits, and the packed `struct vgt_if` shared memory ABI.

## Important APIs, types, and functions

Important constants include `VGT_PVINFO_PAGE`, `VGT_PVINFO_SIZE`, `VGT_MAGIC`, `VGT_VERSION_MAJOR`, `VGT_VERSION_MINOR`, guest-to-vGPU notification enum values for PPGTT and execlist context create/destroy, capability bits `VGT_CAPS_FULL_PPGTT`, `VGT_CAPS_HWSP_EMULATION`, and `VGT_CAPS_HUGE_GTT`, display-ready values, plus `vgtif_offset(x)` and `vgtif_reg(x)`. `struct vgt_if` is the central packed ABI structure.

## Control flow

The header has no executable flow. Guest and host code map or emulate the PVINFO MMIO page, validate magic/version, read capability/resource fields, and write notification or response fields. The `vgtif_reg()` macro converts structure fields into `_MMIO()` register addresses.

## State and persistence behavior

The shared page persists as virtual MMIO state. The upper half contains host-provided identity, capabilities, and assigned aperture/non-mappable GMADR/fence resources. The lower half contains guest-to-host state such as display readiness, notification type, cursor hot spots, PDP values, and execlist context descriptor fields. The structure is `__packed`, so field offsets are ABI and must not drift.

## Dependencies

It depends on Linux types, `_MMIO()` availability from including contexts, and host/guest agreement on GVT ABI semantics. Observed consumers include GVT MMIO tables, GTT handling, vGPU setup, firmware, command parser, scheduler, framebuffer decoder, and `i915_vgpu.c`.

## Integration points

GVT code uses this header to expose PVINFO registers to guests and interpret guest notifications. Guest-side i915 vGPU detection and setup use `VGT_MAGIC`, capabilities, and resource ballooning fields. Display handoff uses `display_ready`, and execlist/PPGTT virtualization uses the notification and descriptor fields.

## Risks

Any layout change breaks guest/host ABI compatibility. The historical misspelling of "balooning" is present in comments only, but field meaning is fixed. Incorrect offset calculations can cause guest writes to hit the wrong virtual register. Resource fields describe only one contiguous region per VM, so code assuming scattered regions would be incompatible with this ABI.

## Test signals

GVT guest boot, vGPU resource ballooning, PPGTT create/destroy notifications, execlist context lifecycle, display owner switch, and migration/restore tests are relevant. Static layout checks against expected offsets are valuable because the structure is a packed MMIO ABI.

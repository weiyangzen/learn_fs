# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/mmio.h

## Purpose
`mmio.h` declares the GVT MMIO emulation interface and generation masks used by the handler table.

## Important APIs, Types, And Functions
It defines device masks (`D_BDW`, `D_SKL`, `D_KBL`, `D_BXT`, `D_CFL`, aggregates), `gvt_mmio_func`, and `struct intel_gvt_mmio_info`. Declarations cover device type detection, render-MMIO-to-engine mapping, MMIO metadata setup/cleanup/iteration/lookup, vGPU MMIO init/reset/cleanup, GPA translation, read/write emulation, default handlers, masked writes, and PM restore helpers.

## Control Flow
No executable flow exists here. The header defines how `mmio.c`, `handlers.c`, `mmio_context.c`, and `kvmgt.c` share MMIO operations and metadata.

## State And Persistence
`struct intel_gvt_mmio_info` records persist in `gvt->mmio.mmio_info_table`; virtual register contents live in `vgpu->mmio.vreg`. Generation masks control which handlers are installed.

## Dependencies And Integration Points
The header includes `linux/types.h`, forward-declares GVT structs, and is used by most GVT MMIO-facing code.

## Risks
Callback signature or generation-mask changes can mis-register handlers across hardware families. Aggregate masks must stay synchronized with `intel_gvt_get_device_type`.

## Test Signals
Compile coverage and runtime confirmation that platform-specific handlers register and MMIO init/read/write/reset/restore paths work.

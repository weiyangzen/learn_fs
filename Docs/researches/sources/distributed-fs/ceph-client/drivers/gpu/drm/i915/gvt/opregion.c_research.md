# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/opregion.c

## Purpose
`opregion.c` creates and emulates the guest IGD OpRegion, including a synthetic VBT mailbox, guest OpRegion base tracking, and SWSCI service handling.

## Important APIs, Types, And Functions
Public functions are `intel_vgpu_init_opregion`, `intel_vgpu_opregion_base_write_handler`, `intel_vgpu_clean_opregion`, and `intel_vgpu_emulate_opregion_request`. Private packed structs model the OpRegion header, BDB headers, child-device config, and synthetic `vbt`.

## Control Flow
Initialization allocates two zeroed pages, writes the `IntelGraphicsMem` signature, sets version/size/mailbox fields, forces LID open, generates a virtual VBT, and copies it into the VBT area. Base writes record two guest GFNs. SWSCI emulation reads SCIC/PARM from guest memory, filters SMI and non-trigger transitions, supports only capability queries, writes zero success for supported capability calls, and clears exit status for unsupported runtime services.

## State And Persistence
Per-vGPU state is `vgpu_opregion(vgpu)->va` plus recorded `gfn[]`. The generated VBT hardcodes DP child devices on ports A-D and no LVDS. Pages persist until `intel_vgpu_clean_opregion`.

## Dependencies And Integration Points
It uses OpRegion constants from `reg.h`, VBT structures from `intel_vbt_defs.h`, guest GPA read/write helpers, KVMGT VFIO region exposure, and config/MMIO handlers for OpRegion/SWSCI writes.

## Risks
The VBT is synthetic and version-sensitive. Runtime SWSCI support is minimal. Guest GFN recording must happen before SWSCI emulation. Hardcoded child device details may drift from guest driver expectations.

## Test Signals
Valid opregion region reads, guest OpRegion/VBT detection, Windows guest display init, correct base GFN recording, supported SWSCI capability queries, unsupported runtime-service failure without crash, and no allocation leaks.

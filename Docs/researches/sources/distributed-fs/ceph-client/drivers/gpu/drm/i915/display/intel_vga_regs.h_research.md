# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga_regs.h

### Purpose
`intel_vga_regs.h` defines display MMIO register addresses and bitfields for the legacy VGA control register variants used by i915 display platforms.

### Important APIs, Types, And Functions
The key register macros are `VGACNTRL`, `VLV_VGACNTRL`, and `CPU_VGACNTRL`. Bitfields include `VGA_DISP_DISABLE`, pre-ILK `VGA_2X_MODE`, pipe selection masks for pre-IVB and CHV, border/CSC/centering/palette controls, legacy 8-bit palette enable, nine-dot disable, and active/blank throttling fields.

### Control Flow
There is no executable flow. `intel_vga.c` selects the platform-specific control register and uses these fields to detect and disable the legacy VGA plane.

### State, Persistence, And Dependencies
The state is hardware MMIO. The header depends on `intel_display_reg_defs.h` for MMIO and bitfield helpers.

### Integration Points
Integrated primarily with `intel_vga_disable()` and any display readback/debug paths that inspect VGA control. Platform conditionals in `intel_vga.c` determine which register and pipe-selection masks apply.

### Risks
Using the wrong pipe-selection mask on CHV or older platforms can misreport the active VGA pipe. Clearing or preserving unrelated bits incorrectly could disturb palette/CSC/centering state, though the current disable path writes only `VGA_DISP_DISABLE`.

### Test Signals
Register dumps before and after `intel_vga_disable()`, platform-specific boot logs for pre-ILK, VLV/CHV, and CPU transcoder platforms, and absence of stuck-pipe behavior on older hardware are useful signals.

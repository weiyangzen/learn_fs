<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.c

## Purpose
`vs_crtc.c` implements VeriSilicon DC CRTC operations: pixel-clock enable/disable, display timing register programming, mode validation/fixup, vblank IRQ enable/disable, and CRTC allocation with a primary plane.

## Important APIs, Types, and Functions
The public entry is `vs_crtc_init()`. Important callbacks are `vs_crtc_atomic_enable()`, `vs_crtc_atomic_disable()`, `vs_crtc_mode_set_nofb()`, `vs_crtc_mode_valid()`, `vs_crtc_mode_fixup()`, `vs_crtc_enable_vblank()`, and `vs_crtc_disable_vblank()`. It uses `struct vs_crtc` and register macros from `vs_crtc_regs.h` and `vs_dc_top_regs.h`.

## Control Flow
Initialization allocates a managed CRTC object, stores DC pointer/output ID, creates a primary plane, initializes the DRM CRTC with that plane, and attaches helper funcs. Mode fixup normalizes CRTC timings and rounds the pixel clock through the output clock. Mode set writes horizontal/vertical display/total/sync registers and applies sync polarity bits, then sets the clock rate. Atomic enable prepares/enables the pixel clock and turns vblank on; disable turns vblank off and disables the pixel clock. Vblank callbacks toggle top-level VSYNC IRQ bits for the output.

## State and Persistence Behavior
Persistent state is the `struct vs_crtc` plus DRM CRTC state. Hardware timing registers and pixel-clock rate persist until the next modeset. Vblank state is maintained by DRM core and IRQ enable bits.

## Dependencies and Integration Points
The file depends on DRM atomic/vblank helpers, common clock APIs, regmap, `vs_primary_plane_init()`, DC top IRQ registers, and the DC identity output count. Bridge enable later starts the output panel that consumes these timings.

## Risks
Timing fields are 15-bit and validation only checks totals, not every start/end relationship. Clock errors are warned in mode set/enable but not always propagated. Vblank handling assumes DC top IRQ status bits line up with output IDs. Primary-plane creation failure aborts CRTC creation.

## Test Signals
Mode validation should cover too-large totals and unroundable clocks. Atomic modeset tests should verify register values, clock rate feedback, enable/disable ordering, vblank IRQ toggling, and multi-output CRTC IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.c -->

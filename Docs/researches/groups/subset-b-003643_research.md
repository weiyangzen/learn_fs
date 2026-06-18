# subset-b-003643 research

Grouped research for Meson VENC/VIU/VPP, Matrox mgag200 KMS, and MSM Adreno A2xx build/catalog files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_venc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_venc.c

## Purpose
Implements the Amlogic Meson video encoder programming layer for CVBS, HDMI/TMDS, and MIPI DSI/LCD-style output paths. It translates DRM display modes and HDMI VICs into ENCI, ENCP, and ENCL hardware register programming and maintains the active VENC mode state used by interrupt and encoder code.

## Important APIs, types, and functions
- Global CVBS tables `meson_cvbs_enci_pal` and `meson_cvbs_enci_ntsc` provide PAL/NTSC ENCI timing and analog adjustment parameters.
- `union meson_hdmi_venc_mode` holds either ENCI interlace timing fields or ENCP progressive/interlace timing fields for HDMI.
- Static `meson_hdmi_venc_vic_modes[]` maps CEA VICs to precomputed ENCI/ENCP timing tables for 480i/576i, 480p/576p, 720p, 1080i/p, and 2160p modes.
- Exported HDMI helpers: `meson_venc_hdmi_supported_mode()`, `meson_venc_hdmi_supported_vic()`, `meson_venc_hdmi_venc_repeat()`, and `meson_venc_hdmi_mode_set()`.
- LCD/DSI helpers: `meson_encl_load_gamma()` and `meson_venc_mipi_dsi_mode_set()`.
- CVBS helpers: `meson_venci_cvbs_mode_set()` and `meson_venci_get_field()`.
- Lifecycle/IRQ helpers: `meson_venc_enable_vsync()`, `meson_venc_disable_vsync()`, and `meson_venc_init()`.

## Control flow
HDMI mode setup first decides whether to use ENCI or ENCP. Double-clocked interlaced modes use ENCI and HDMI read-rate repetition; known VICs use static timing tables; unknown but otherwise valid DMT modes synthesize a simple ENCP timing block from `struct drm_display_mode`. Pixel counts, active region, porch, sync width, and field-line counts are adjusted for HDMI repeat, VENC repeat, YUV420, and interlace. The function disables VDAC and both ENCI/ENCP, programs the selected encoder, computes DE/HSYNC/VSYNC windows, selects the VIU/VPP mux, writes `VPU_HDMI_SETTING`, records repeat/use-ENCI flags, and marks `priv->venc.current_mode` as HDMI.

The ENCI path programs CVBS-like timing, ENCI FIFO-to-video settings, top/bottom field windows, DVI sync windows, and interlaced field-specific VSYNC registers. The ENCP path writes the table or synthesized ENCP mode fields, enables ENCP, programs DE and DVI sync timing for even and optionally odd fields, then selects ENCP in the VPP mux.

MIPI DSI mode setup selects ENCL, disables ENCL, derives all horizontal and vertical timing from the DRM mode, configures ENCL video, test pattern, dithering, TTL/TCON DE/HSYNC/VSYNC outputs, gamma coefficient base registers, and sets the current mode to MIPI DSI. CVBS setup skips reprogramming when the requested PAL/NTSC tag is already active, then programs ENCI, VDAC, upsamplers, DAC selections, saturation/contrast/brightness/hue, and analog sync adjustment.

Initialization powers down VDAC and HDMI PHY registers via HHI regmap, disables HDMI routing and all encoders, disables VSync IRQ generation, and resets the current mode to none. VSync enable chooses ENCP line-reset interrupt only for MIPI DSI and ENCI line-reset for the other modes.

## State and persistence
The durable runtime state lives in `priv->venc`: `current_mode`, `hdmi_repeat`, `venc_repeat`, and `hdmi_use_enci`. The file also leaves persistent hardware state in VPU/VENC MMIO registers and HHI regmap registers until another modeset or `meson_venc_init()` rewrites them. Gamma loading writes 256-entry linear LUT data separately for R, G, and B and enables the ENCL gamma control port.

## Dependencies and integration points
Depends on Linux MMIO helpers, regmap for HHI, DRM display mode flags, Meson register definitions, `meson_vpu_is_compatible()`, and `meson_vpp_setup_mux()`. It is called by Meson HDMI, CVBS, and DSI encoder implementations and by the CRTC/IRQ path that needs VSync control and field polarity.

## Risks
The HDMI timing tables are hardware-specific magic values; small changes can break sync on specific TVs or CEA modes. ENCI/ENCP repeat handling is subtle because HDMI FIFO read/write rates, VENC pixel doubling, interlace field math, and YUV420 all interact. DMT fallback accepts a broad mode range but uses a minimal synthesized ENCP timing path that may not match all monitor expectations. Gamma programming uses polling with warning-only timeout handling, so display output may continue with stale gamma if the hardware is not ready. `meson_venci_cvbs_mode_set()` is idempotent by mode tag, which can skip reprogramming after external register corruption.

## Test signals
Useful validation includes HDMI mode coverage for each mapped VIC, DMT fallback modes, 480i/576i double-clocked ENCI output, YUV420 FIFO rate handling, PAL/NTSC CVBS output, MIPI DSI panel timings, VSync IRQ selection, suspend/resume reinitialization, and `priv->venc` repeat/use-ENCI state observed by HDMI clock/encoder code. Register dumps around `VPU_HDMI_SETTING`, ENCI/ENCP DE/VSYNC registers, and HHI VDAC/PHY controls are high-value debugging signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_venc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_venc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_venc.h

## Purpose
Declares the Meson video encoder public interface shared by the Meson DRM encoder, CRTC, and mode-setting code.

## Important APIs, types, and functions
- Defines VENC mode tags: none, CVBS PAL, CVBS NTSC, HDMI, and MIPI DSI.
- Defines `struct meson_cvbs_enci_mode`, the PAL/NTSC ENCI timing and analog parameter structure consumed by CVBS setup.
- Declares external PAL/NTSC timing tables.
- Declares HDMI validation and setup APIs, ENCL gamma loading, CVBS setup and field readout, VSync control, and VENC initialization.

## Control flow
The header has no runtime control flow. It exposes a narrow API that lets output-specific encoder files request mode programming while keeping HDMI timing tables and register programming internals private to `meson_venc.c`.

## State and persistence
No state is stored here. The declared functions mutate `struct meson_drm` VENC state and VPU/HHI hardware registers.

## Dependencies and integration points
Forward references `struct drm_display_mode` and relies on `struct meson_drm` being visible to includers. It is an integration point for Meson HDMI, CVBS, DSI, and CRTC/IRQ code.

## Risks
The `struct meson_cvbs_enci_mode` layout is a direct contract with the implementation's register writes. Adding fields or reordering without updating all tables would silently corrupt CVBS programming.

## Test signals
Build coverage catches signature drift. Runtime coverage comes from callers successfully linking to HDMI/CVBS/DSI mode setup and VSync control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_venc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_viu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_viu.c

## Purpose
Initializes and controls the Meson Video Input Unit OSD path, including OSD color-space conversion matrices, EOTF/OETF LUTs, OSD1 reset recovery, and AFBC path selection for GXM/G12A-class SoCs.

## Important APIs, types, and functions
- Internal enums `viu_matrix_sel_e` and `viu_lut_sel_e` select OSD matrix/LUT blocks.
- Static coefficient tables include RGB709-to-limited-YUV709 matrix, EOTF bypass matrix, linear EOTF 33-entry LUT, and linear OETF 41-entry LUT.
- Matrix/LUT writers: `meson_viu_set_g12a_osd1_matrix()`, `meson_viu_set_osd_matrix()`, `meson_viu_set_osd_lut()`, and `meson_viu_load_matrix()`.
- Public helpers: `meson_viu_osd1_reset()`, `meson_viu_g12a_enable_osd1_afbc()`, `meson_viu_g12a_disable_osd1_afbc()`, `meson_viu_gxm_enable_osd1_afbc()`, `meson_viu_gxm_disable_osd1_afbc()`, and `meson_viu_init()`.

## Control flow
Initialization disables OSD1 and OSD2, then loads the appropriate matrix path by SoC family. GXL/GXM use the older VIU OSD matrix/EOTF/OETF path; G12A uses the VPP wrapper OSD1 matrix and clears vendor bootloader HDR2 state that can cause color distortion. It then programs OSD FIFO priorities, burst lengths, hold lines, alpha replacement values, disables VD1 AFBC, initializes VD luma FIFO sizes, and for G12A sets blend routing, Dolby bypass, dummy blend data, and disables AFBCD.

The OSD1 reset helper saves two OSD control registers, toggles VIU software reset, restores the saved registers, and reloads color conversion state as a workaround for a GXL+ alpha OSD issue. AFBC enable on G12A enables Mali AFBC unpack, chooses ARGB or ABGR reorder based on `priv->afbcd.format`, and routes OSD1 through the AFBCD path. GXM AFBC control is a simpler write to `VIU_MISC_CTRL1`.

## State and persistence
The file initializes `priv->viu.osd1_enabled`, `osd1_commit`, and `osd1_interlace` to false. AFBC enable depends on `priv->afbcd.format`. Most state is persistent hardware register state in VIU, VPP wrapper, OSD blend, Dolby, FIFO, matrix, and LUT registers.

## Dependencies and integration points
Depends on Meson compatibility detection, register definitions, DRM fourcc formats, and Linux bitfield helpers. It is used by Meson driver initialization, plane/AFBCD paths, and reset workarounds needed by OSD scanout.

## Risks
Matrix and LUT programming is register-layout-sensitive, with different control bits for legacy VIU and G12A wrapper paths. The G12A color-distortion workaround clears vendor bootloader state and is easy to regress if compatibility checks change. AFBC reorder only switches for XBGR/ABGR; unsupported formats could display swapped channels. OSD reset preserves only two registers and then reloads matrices, so any additional volatile state lost across reset would need explicit restore.

## Test signals
Validate OSD scanout colors on GXL, GXM, and G12A, especially RGB-to-YUV limited range output and the green/pink distortion workaround. AFBC test signals include correct channel order for ARGB and ABGR/XBGR formats, clean enable/disable transitions, and no stale OSD blend routing after init or reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_viu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_viu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_viu.h

## Purpose
Defines Meson VIU OSD register bit fields and declares VIU initialization, OSD1 reset, and AFBC routing helpers.

## Important APIs, types, and functions
- OSD block configuration macros cover Mali source enable, canvas select, endianness, block modes, RGB/YUV output, color matrix encodings, and Mali AFBC color modes.
- OSD control macros cover enable bits, linear address mode, global alpha shift, AFBCD data path, alpha replacement, and pending status.
- Declares `meson_viu_osd1_reset()`, G12A/GXM AFBC enable/disable functions, and `meson_viu_init()`.

## Control flow
No runtime control flow exists in the header. Plane code and VIU implementation code include these constants to compose register values.

## State and persistence
No state is stored. Constants describe hardware register values that persist after writes performed by implementation and plane code.

## Dependencies and integration points
Depends on `BIT()` from kernel headers via includers and on `struct meson_drm` declarations from the broader Meson driver. It is coupled to `meson_viu.c`, Meson plane programming, and AFBCD support.

## Risks
These macros encode hardware ABI. Incorrect block mode, channel matrix, or AFBCD path bit values will cause wrong colors, broken scanout, or missing AFBC output.

## Test signals
Build coverage for macro use, plus runtime plane-format tests for RGB565/RGB888/XRGB8888 and AFBC formats that exercise these register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_viu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vpp.c

## Purpose
Initializes the Meson Video Post Processing block, including output muxing, postblend/preblend defaults, FIFO sizing, scaler disabling, and scaler filter coefficient programming.

## Important APIs, types, and functions
- `meson_vpp_setup_mux()` writes the VIU-to-VENC mux control register.
- Static OSD four-point B-spline and video bicubic coefficient tables provide 33 coefficient entries for horizontal and vertical scaler filters.
- `meson_vpp_write_scaling_filter_coefs()` and `meson_vpp_write_vd_scaling_filter_coefs()` program OSD and video scaler coefficient ports.
- `meson_vpp_init()` performs SoC-specific VPP initialization.

## Control flow
Initialization first programs dummy black data and Dolby-path settings by SoC compatibility: GXL, GXM, and G12A have different defaults. It sets output FIFO size and hold lines, disables preblend/postblend and all blend sources on non-G12A hardware, seeds default VD ranges, disables OSD scalers, enables video scale-out bank length defaults, enables VADJ minus black level, and writes both OSD and VD horizontal/vertical filter coefficients.

## State and persistence
No C-side state is kept in this file. VPP state persists in VPU MMIO registers until another init or modeset path updates it. The mux register determines which VENC block receives post-processed VIU output.

## Dependencies and integration points
Depends on Meson compatibility checks and register definitions. `meson_venc.c` calls `meson_vpp_setup_mux()` when selecting ENCI, ENCP, or ENCL. Plane and CRTC code rely on `meson_vpp_init()` defaults before enabling OSD scanout.

## Risks
SoC-specific defaults are compatibility-sensitive; incorrect dummy data, Dolby bypass, or blend setup can produce black screens or wrong color on one family while working on another. The header declares interlace scaler helpers that are not implemented in this file, so callers must link against another implementation or avoid those declarations in this tree revision.

## Test signals
Validate clean boot display on GXL/GXM/G12A, correct ENCI/ENCP/ENCL mux selection during mode changes, scaler-disabled baseline output, and absence of unexpected preblend/postblend video paths. Register dumps of `VPP_MISC`, `VPP_OFIFO_SIZE`, `VPU_VIU_VENC_MUX_CTRL`, and scaler coefficient ports are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vpp.h

## Purpose
Declares VPP mux values and initialization/scaler APIs for the Meson post-processing block.

## Important APIs, types, and functions
- Defines mux values for ENCL (`0x0`), ENCI (`0x5`), and ENCP (`0xA`).
- Declares `meson_vpp_setup_mux()`, interlace OSD1 vertical scaler enable/disable helpers, and `meson_vpp_init()`.

## Control flow
No runtime control flow exists in the header. It provides constants and function declarations used by VENC and display initialization paths.

## State and persistence
No state is stored. Mux constants represent persistent hardware routing values once written.

## Dependencies and integration points
Forward declares `struct drm_rect` and `struct meson_drm`. It is included by VPP implementation and by VENC code to switch output routing.

## Risks
Wrong mux constants route VIU output to the wrong encoder. The interlace scaler declarations create a link-time contract that must be satisfied elsewhere in the full driver.

## Test signals
Build/link coverage and runtime validation that HDMI, CVBS, and DSI modes select the expected encoder path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/Kconfig

## Purpose
Defines kernel configuration options for the Matrox G200 DRM/KMS driver and its optional write-combine disable mode.

## Important APIs, types, and functions
- `DRM_MGAG200` is a tristate depending on DRM and PCI and selecting client selection, GEM shmem helpers, KMS helpers, I2C, and I2C algobit.
- `DRM_MGAG200_DISABLE_WRITECOMBINE` is a PREEMPT_RT-specific bool that disables write-combine VRAM mappings.

## Control flow
This is build-time configuration only. Enabling `DRM_MGAG200` builds the mgag200 object. The write-combine option changes the VRAM mapping branch in `mgag200_device_preinit()`.

## State and persistence
No runtime state. The selected configuration persists in the kernel build and changes driver mapping behavior.

## Dependencies and integration points
Integrates with the DRM, PCI, KMS helper, GEM shmem, I2C, and I2C algobit subsystems. The write-combine toggle is consumed through `CONFIG_DRM_MGAG200_DISABLE_WRITECOMBINE`.

## Risks
Disabling write-combine can reduce framebuffer update performance but may be needed on real-time systems. Missing I2C selections would break DDC support, so the selects are part of the driver contract.

## Test signals
Configuration tests should cover module and built-in builds, PREEMPT_RT builds with write-combine disabled, and dependency resolution through `make olddefconfig` or similar Kconfig checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/Makefile

## Purpose
Defines the object list for the mgag200 DRM driver.

## Important APIs, types, and functions
- `mgag200-y` includes shared core files, DDC/BMC support, all chip-specific G200 variants, mode-setting code, and VGA/BMC connector files.
- `obj-$(CONFIG_DRM_MGAG200) += mgag200.o` links the composite object when configured.

## Control flow
Build-system control flow only. Kbuild compiles every listed object into `mgag200.o` when `DRM_MGAG200` is enabled.

## State and persistence
No runtime state. The file determines which source modules are present in the final kernel object.

## Dependencies and integration points
Pairs with `Kconfig` and with prototypes in `mgag200_drv.h`; every chip factory referenced by `mgag200_drv.c` must have an object listed here.

## Risks
Omitting a variant object would create link failures or unsupported PCI IDs. Adding new chip support requires updating this file, the PCI ID table, and shared declarations together.

## Test signals
Build coverage for `CONFIG_DRM_MGAG200=m` and `=y` is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_bmc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_bmc.c

## Purpose
Implements coordination with a server BMC that may remotely scan out the same Matrox framebuffer during mode changes.

## Important APIs, types, and functions
- `mgag200_bmc_stop_scanout()` signals an upcoming mode change, masks remote scan requests, and waits for remote scan/frame status.
- `mgag200_bmc_start_scanout()` resets remote-head level 2, unmasks scan requests, and clears the GPIO signal.

## Control flow
Stop scanout configures DAC GPIO misc bit 0 as output, drives it high to notify the BMC, sets `MGA1064_SPAREREG` bit 7 to mask remote scan requests, waits for `remhsyncsts` to go low, and if active waits for `remvsyncsts`. Start scanout asserts/deasserts `rstlvl2`, clears the scan request mask, and drives the misc line low again.

## State and persistence
State is stored in DAC indirect GPIO, spare, and remote-head control registers. These bits persist until start/stop toggles them or firmware/hardware changes them.

## Dependencies and integration points
Called by the BMC-aware VGA encoder helper in `mgag200_vga_bmc.c` when `mdev->info->sync_bmc` is true. Uses DAC register access macros from `mgag200_drv.h` and polling helpers.

## Risks
The protocol uses undocumented/board-specific DAC GPIO bits and timeout-based polling. If the BMC does not follow the expected handshake, stop may time out and return without guaranteeing scanout quiescence. Register access must be serialized by the caller's modeset lock path.

## Test signals
Server platforms with active BMC remote console should modeset without tearing or BMC lockups. Poll timeout behavior, remote console continuity, and correct restoration after disable/enable are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_bmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_ddc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_ddc.c

## Purpose
Creates a bit-banged I2C adapter over Matrox DAC GPIO lines for VGA DDC/EDID reads.

## Important APIs, types, and functions
- `struct mgag200_ddc` stores the `mga_device`, data/clock bit masks, `i2c_algo_bit_data`, and `i2c_adapter`.
- GPIO helpers `mga_i2c_read_gpio()`, `mga_i2c_set_gpio()`, and `mga_i2c_set()` manipulate DAC generic I/O registers.
- I2C algorithm callbacks implement setsda, setscl, getsda, getscl, pre_xfer, and post_xfer.
- `mgag200_ddc_create()` allocates, initializes, registers, and devm-manages the adapter.

## Control flow
Creation initializes DAC generic I/O registers, derives the data and clock masks from `mdev->info->i2c`, fills bit-bang callbacks and timings, names the adapter, registers it with `i2c_bit_add_bus()`, and installs a DRM-managed cleanup action. Each transfer locks `mdev->rmmio_lock`, bit-bangs GPIO, then unlocks.

## State and persistence
Adapter state persists for the DRM device lifetime through DRM-managed allocation. Hardware GPIO direction/data registers persist and are shared with DDC and BMC signaling paths.

## Dependencies and integration points
Depends on Linux I2C algobit, DRM managed resources, PCI/device parenting, and mgag200 register macros. Used by both plain VGA and BMC-aware VGA connector initialization.

## Risks
The GPIO semantics invert output state in `mga_i2c_set()`, so changes can easily break open-drain behavior. DDC transfers must remain serialized against modesetting because DAC indexed registers are shared. Wrong `i2c.data_bit` or `clock_bit` in device info causes EDID failure.

## Test signals
EDID read success, connector hotplug detection, fallback modes when EDID is absent, and absence of races with concurrent modesets are the main signals. I2C adapter registration failures should be visible in DRM error logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_ddc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_ddc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_ddc.h

## Purpose
Declares the mgag200 DDC adapter creation API.

## Important APIs, types, and functions
- Forward declares `struct i2c_adapter` and `struct mga_device`.
- Declares `struct i2c_adapter *mgag200_ddc_create(struct mga_device *mdev);`.

## Control flow
No runtime control flow. Connector initialization calls the declared function to get an I2C adapter for DDC.

## State and persistence
No state is stored in the header. The implementation creates DRM-managed adapter state.

## Dependencies and integration points
Included by VGA connector files and `mgag200_mode.c`. Keeps DDC implementation details private.

## Risks
Signature drift would break connector initialization at build time.

## Test signals
Build coverage and successful EDID probing through connectors using `mgag200_ddc_create()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_ddc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_drv.c

## Purpose
Provides the mgag200 PCI DRM driver entry point, shared device preinitialization, VRAM probing, DRM driver registration, and PCI ID dispatch to chip-specific device factories.

## Important APIs, types, and functions
- Module parameter `modeset` gates driver registration through `drm_module_pci_driver_if_modeset`.
- `mgag200_init_pci_options()` writes Matrox PCI option registers.
- `mgag200_probe_vram()` probes usable VRAM by alias testing.
- `mgag200_device_preinit()` maps BAR1 MMIO and BAR0 VRAM, optionally using write-combine.
- `mgag200_device_init()` sets shared device info/functions, initializes the MMIO lock, enables MGA mode, RAM map, high page select, and disables interrupts.
- `mgag200_pci_probe()` dispatches PCI IDs to per-chip create functions and registers the DRM device.
- Remove/shutdown paths unregister and atomically shut down the DRM device.

## Control flow
Probe removes conflicting framebuffers, enables the PCI device, switches on the `enum mga_type` stored in the PCI ID table, calls the selected factory, registers the resulting DRM device, and starts the generic DRM client with XRGB8888. Chip factories perform PCI option setup, resource mapping, shared device init, chip register init, VRAM probe, mode config init, pipeline init, mode config reset, and polling setup.

## State and persistence
PCI driver data stores the DRM device. `struct mga_device` persists MMIO/VRAM resource mappings, available VRAM, locks, output objects, and selected device info/function tables. Hardware PCI options and core MGA registers persist beyond individual atomic commits.

## Dependencies and integration points
Depends on PCI, aperture conflict removal, DRM managed allocation, GEM shmem/fbdev helpers, DRM atomic helpers, and all per-chip factory functions declared in `mgag200_drv.h`. It is the root integration point for the whole mgag200 driver.

## Risks
VRAM probing writes test patterns into MMIO VRAM and relies on restoring sampled values; aliasing or unusual BAR sizing can misreport memory. Device type dispatch must match PCI IDs and object list. Write-combine mapping is performance-sensitive and has PREEMPT_RT implications. The driver forces XRGB8888 client setup due to known 24-bit depth issues on G200ER.

## Test signals
PCI bind/unbind, framebuffer handoff, module parameter behavior, BAR mapping failures, VRAM size logs, DRM device registration, fbdev/client startup, and shutdown during reboot or module unload are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_drv.h

## Purpose
Defines the shared mgag200 driver ABI: register access macros, driver metadata, device state structures, chip capability tables, PLL state, and cross-file function prototypes.

## Important APIs, types, and functions
- MMIO/DAC/VGA indexed register macros: `RREG8`, `WREG8`, `RREG32`, `WREG32`, `RREG/WREG_*` for MISC, ATTR, SEQ, CRT, ECRT, GFX, and DAC.
- `MGAG200_DAC_DEFAULT()` centralizes default DAC register tables used by chip-specific init files.
- `struct mgag200_pll_values` stores m/n/p/s PLL parameters.
- `struct mgag200_crtc_state` extends `drm_crtc_state` with primary format, PIXPLLC values, and BMC video-reset flag.
- `enum mga_type` enumerates PCI-dispatched chip variants.
- `struct mgag200_device_info` captures max mode size, bandwidth cap, BMC sync flag, I2C GPIO bits, and `bug_no_startadd`.
- `struct mgag200_device_funcs` supplies per-chip PLL atomic check/update callbacks.
- `struct mga_device` embeds the DRM device and core resources/output objects.
- Helper macros assemble shared plane and CRTC function tables.

## Control flow
Header macros expand into indexed MMIO register operations used throughout the driver. The function table macros define the common atomic helper behavior used by per-chip pipeline initialization.

## State and persistence
The structures define persistent driver state for the DRM device lifetime. Register macros mutate persistent hardware state and depend on a local `mdev` variable convention in callers.

## Dependencies and integration points
Includes DRM connector/CRTC/encoder/GEM/plane headers and `mgag200_reg.h`. All mgag200 C files depend on this header for shared types and prototypes.

## Risks
The register macros are not type-safe and assume `mdev` exists in scope. Indexed DAC/VGA access is shared by DDC, modesetting, BMC, and PLL paths and must be serialized. `MGAG200_DAC_DEFAULT()` is a dense table of magic values that affects every chip init path.

## Test signals
Build coverage across all variants, lockdep/race testing around MMIO access, and runtime modeset/EDID/PLL validation all exercise this header's contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200.c

## Purpose
Implements support for original Matrox G200 PCI/AGP devices, including PCI option setup, BIOS-derived clock limits, PIXPLLC calculation/programming, pipeline creation, and device factory construction.

## Important APIs, types, and functions
- `mgag200_g200_init_pci_options()` chooses PCI option values based on SGRAM presence.
- `mgag200_g200_init_registers()` writes default DAC state and shared VGA registers.
- `mgag200_g200_pixpllc_atomic_check()` searches m/n/p/s PLL values using BIOS-derived reference and pixel clock limits.
- `mgag200_g200_pixpllc_atomic_update()` writes PIXPLLC set C registers and selects MGA clock.
- `mgag200_g200_interpret_bios()` parses Matrox PInS BIOS structures to adjust pclk/refclk values.
- `mgag200_g200_device_create()` constructs the full DRM device.

## Control flow
Factory allocation stores PCI driver data, initializes PCI options, maps resources, initializes reference clock defaults and optionally overrides them from PCI ROM PInS data, initializes shared device state, programs chip registers, probes VRAM, initializes mode config and a VGA output pipeline, resets mode config, and starts connector polling.

## State and persistence
`struct mgag200_g200_device` adds `ref_clk`, `pclk_min`, and `pclk_max` to shared `mga_device`. Computed PLL values persist in `mgag200_crtc_state` until atomic update writes DAC PLL registers. PCI option and DAC register state persist in hardware.

## Dependencies and integration points
Uses DRM atomic/plane/CRTC helpers, PCI ROM mapping, vmalloc, and shared mgag200 mode/DDC/VGA helpers. Called from `mgag200_pci_probe()` for G200_PCI and G200_AGP.

## Risks
BIOS PInS parsing accepts multiple versions and silently returns on malformed data; wrong limits can reject valid modes or overclock. PLL search clamps low clocks and relies on magic p/s thresholds. The original G200 uses plain VGA output, unlike server variants that use the BMC-aware connector path.

## Test signals
Original G200 PCI/AGP hardware should expose EDID modes, accept clocks within BIOS limits, and produce stable output across 8/16/24/32 bpp formats. Debug logs for PInS and PLL parameters are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh.c

## Purpose
Implements the G200EH server variant, including shared EH register defaults, 33.333 MHz PLL search, PLL lock programming sequence, BMC-aware VGA pipeline, and device factory.

## Important APIs, types, and functions
- `mgag200_g200eh_init_registers()` is also reused by EH3/EH5.
- `mgag200_g200eh_pixpllc_atomic_check()` searches m/n/p for a 400-800 MHz VCO.
- `mgag200_g200eh_pixpllc_atomic_update()` powers down/reprograms the EH PLL, selects PLL output, re-enables the clock, and polls `MGAREG_VCOUNT` for lock.
- `mgag200_g200eh_device_create()` creates the EH DRM device.

## Control flow
Atomic check stores PLL values in CRTC state. Atomic enable uses the common CRTC helper, which calls the EH PLL updater after mode register programming. The update loop tries up to 33 programming attempts and treats vertical-count progress as lock indication.

## State and persistence
Device info caps modes at 2048x2048 and 37.5 GiB/s-style bandwidth units as used by the driver. PLL values persist in CRTC state and hardware DAC PLL registers. The BMC-aware VGA connector can signal BMC coordination based on `sync_bmc`, which is false for this info table.

## Dependencies and integration points
Reuses shared mgag200 KMS helpers, BMC-aware VGA output initialization, and shared EH init/update routines for later EH variants.

## Risks
PLL locking uses polling heuristics rather than a direct lock bit. The update function does not return an error if it fails to observe lock. EH register defaults skip specific DAC ranges, so changes can disturb variant compatibility.

## Test signals
Modeset stability on G200EH, debug/trace inspection of PLL retries, EDID fallback behavior, and successful output after repeated mode switches are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh3.c

## Purpose
Adds support for G200EH3 using a custom PLL search while reusing G200EH register initialization and PLL programming.

## Important APIs, types, and functions
- `mgag200_g200eh3_pixpllc_atomic_check()` searches testm/testn within a 1.5-3.0 GHz VCO envelope and stores adjusted m/n/p values.
- `mgag200_g200eh3_pipeline_init()` builds the shared primary plane, CRTC, color management, and BMC-aware VGA output.
- `mgag200_g200eh3_device_create()` wires EH3 device info and funcs into the shared factory sequence.

## Control flow
Factory setup follows the EH pattern: PCI options, resource mapping, shared init, EH register defaults, VRAM probe, mode config, pipeline, reset, and polling. Atomic update is delegated to `mgag200_g200eh_pixpllc_atomic_update()`.

## State and persistence
No extra C struct beyond `mga_device`. Device info allows 2048x2048 with no bandwidth cap. PLL state is stored in `mgag200_crtc_state` and programmed by the shared EH updater.

## Dependencies and integration points
Depends on EH helpers declared in `mgag200_drv.h` and shared mgag200 KMS helpers. Dispatched from the PCI ID table for device ID 0x538.

## Risks
The PLL search initializes `testp` to zero and stores `p = testp + 1`, reflecting this variant's encoding; changing it like other variants would break clocks. No acceptable-delta check is performed.

## Test signals
G200EH3 hardware modeset across low and high pixel clocks, PLL lock behavior through the shared EH update loop, and connector fallback modes are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh5.c

## Purpose
Adds support for G200EH5 using a newer high-frequency PLL formula while reusing G200EH register initialization and PLL programming.

## Important APIs, types, and functions
- `mgag200_g200eh5_pixpllc_atomic_check()` searches multiplier and divider A/B values using 25 MHz reference, 2.5-10 GHz VCO bounds, and stores encoded values in `mgag200_pll_values`.
- `mgag200_g200eh5_pipeline_init()` creates the shared KMS plane/CRTC/gamma and BMC-aware VGA output.
- `mgag200_g200eh5_device_create()` constructs the DRM device for PCI ID 0x53a.

## Control flow
The PLL check iterates multiplier 100..400, divider A 8..1, divider B 1..A, computes output frequency in Hz, and keeps the minimum delta. The factory then follows the EH pattern and uses `mgag200_g200eh_pixpllc_atomic_update()` to program the encoded values.

## State and persistence
No extra device state. Encoded PLL values persist in atomic CRTC state and hardware DAC PLL registers. Device info allows 2048x2048 with no bandwidth cap.

## Dependencies and integration points
Uses Linux units constants, DRM helpers, shared EH init/update functions, and BMC VGA output.

## Risks
The check stores encoded byte values plus one into a generic m/n/p container, then relies on the EH updater's subtract-one behavior. That encoding is non-obvious and fragile. There is no explicit failure if the best frequency delta is large.

## Test signals
Pixel clock accuracy on EH5, successful lock through the EH update loop, and modeset coverage for common server resolutions are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200eh5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200er.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200er.c

## Purpose
Implements G200ER support with ER-specific register defaults, tag FIFO reset, PLL programming sequence, and a custom CRTC enable path.

## Important APIs, types, and functions
- `mgag200_g200er_init_registers()` writes default DAC state and ER-specific DAC/ECRT registers.
- `mgag200_g200er_reset_tagfifo()` toggles an undocumented `MGAREG_MEMCTL` reset bit.
- `mgag200_g200er_pixpllc_atomic_check()` searches r/n/m/o values for a 48 MHz reference and 1.056-1.488 GHz VCO.
- `mgag200_g200er_pixpllc_atomic_update()` disables pixel/remote clocks, powers the PLL down, writes ER PLL registers, and delays.
- Custom `mgag200_g200er_crtc_helper_atomic_enable()` resets the tag FIFO after PLL programming.

## Control flow
The factory maps and initializes the device, probes VRAM, configures mode limits, creates the pipeline, and starts polling. During atomic enable, the custom helper programs format and mode, updates PIXPLLC, resets the tag FIFO, loads gamma, and enables display.

## State and persistence
Device info caps 2048x2048 and bandwidth 55000 with BMC sync disabled. PLL values persist in CRTC state. ER-specific DAC, ECRT, and MEMCTL state persists in hardware.

## Dependencies and integration points
Uses shared KMS helpers and BMC-aware VGA output. Dispatched for PCI ID 0x534.

## Risks
The tag FIFO reset uses an undocumented magic bit. PLL update does not explicitly re-enable every clock bit it disables in the same way as other variants, relying on later display enable/clock state. A comment in the main driver forces XRGB8888 because 24 bpp is known problematic on G200ER.

## Test signals
G200ER should be tested with XRGB8888 client setup, repeated modesets, tag FIFO reset behavior, EDID/no-EDID paths, and high-bandwidth mode rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200er.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200ev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200ev.c

## Purpose
Implements G200EV support with EV-specific register initialization, 50 MHz reference PLL search/programming, high-priority level setup, custom CRTC enable, and device factory.

## Important APIs, types, and functions
- `mgag200_g200ev_init_registers()` writes EV default DAC values and shared VGA registers.
- `mgag200_g200ev_set_hiprilvl()` clears ECRT 0x06.
- `mgag200_g200ev_pixpllc_atomic_check()` searches n/m/p values for a 150-550 MHz VCO.
- `mgag200_g200ev_pixpllc_atomic_update()` disables the pixel clock, toggles PLL status/power, writes EV PLL registers, selects PLL, and re-enables output.
- Custom `mgag200_g200ev_crtc_helper_atomic_enable()` inserts hiprilvl setup after PLL update.

## Control flow
Factory setup uses fixed PCI options, shared resource/init code, EV register defaults, VRAM probe, mode config, pipeline init, reset, and polling. Atomic enable follows common register/gamma/display sequencing with an EV-specific high-priority register write.

## State and persistence
Device info sets max 2048x2048, bandwidth 32700, BMC sync false, and DDC bits 0/1. PLL and ECRT state persist in hardware.

## Dependencies and integration points
Uses shared mgag200 mode, DDC, and BMC-aware VGA helpers. Dispatched for PCI ID 0x530.

## Risks
PLL update relies on ordered delays and status-bit manipulation. No delta threshold is enforced in PLL search. Incorrect hiprilvl setup can affect memory arbitration and scanout stability.

## Test signals
Stable EV output across common modes, PLL frequency accuracy, no flicker after mode changes, EDID reads using data bit 0/clock bit 1, and bandwidth validation are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200ev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200ew3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200ew3.c

## Purpose
Implements G200EW3 support by reusing G200WB register/PLL programming with EW3-specific PLL search, register tweak, BMC synchronization, and reduced VRAM probing.

## Important APIs, types, and functions
- `mgag200_g200ew3_init_registers()` calls `mgag200_g200wb_init_registers()` and writes ECRT 0x34.
- `mgag200_g200ew3_pixpllc_atomic_check()` searches two post-dividers plus m/n for a 25 MHz reference and 400-800 MHz VCO.
- Device funcs reuse `mgag200_g200wb_pixpllc_atomic_update()`.
- `mgag200_g200ew3_device_probe_vram()` reserves 4 MiB from BAR size before probing when BAR is at least 16 MiB.

## Control flow
Factory setup writes WB-style PCI options, maps resources, initializes EW3 info/functions, writes registers, probes reduced VRAM, configures KMS, creates a BMC-aware pipeline, and starts polling.

## State and persistence
Device info enables `sync_bmc`, so encoder atomic checks set `set_vidrst` and enable/disable handshakes with the BMC. PLL values persist in atomic state and WB-style hardware PLL registers. Reduced VRAM availability persists in `mdev->vram_available`.

## Dependencies and integration points
Depends on G200WB exported init/update helpers and shared mgag200 KMS/BMC code. Dispatched for PCI ID 0x536.

## Risks
VRAM reservation logic assumes high BAR space includes a 4 MiB region unavailable for scanout. The PLL search is expensive and lacks a delta threshold. BMC sync changes mode register programming through `set_vidrst`.

## Test signals
EW3 hardware should validate BMC remote console handoff, no scanout into reserved VRAM, common modes up to 2048x2048, and stable output with the WB PLL updater.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200ew3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200se.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200se.c

## Purpose
Implements G200SE A/B server variants, including revision detection, revision-specific device limits, two PLL algorithms, high-priority memory arbitration setup, BMC-aware output, and device construction.

## Important APIs, types, and functions
- `mgag200_g200se_init_pci_options()` preserves SGRAM option bit while applying SE PCI options.
- `mgag200_g200se_init_registers()` writes SE DAC defaults.
- `mgag200_g200se_set_hiprilvl()` computes ECRT 0x06 priority by unique revision, mode clock, and format bpp.
- `mgag200_g200se_00_pixpllc_atomic_check/update()` supports older revisions with 160-320 MHz VCO and 25 MHz reference.
- `mgag200_g200se_04_pixpllc_atomic_check/update()` supports revision >= 0x04 with doubled clock and 800-1600 MHz VCO.
- `mgag200_g200se_init_unique_rev_id()` reads model/revision from MMIO 0x1e24.
- `mgag200_g200se_device_create()` selects info and funcs by PCI type and unique revision.

## Control flow
Factory setup initializes PCI options and resources, reads `unique_rev_id`, selects A/B and revision-specific max resolution/bandwidth/bug flags, selects old or rev04 PLL funcs, performs shared init, register init, VRAM probe, mode config, pipeline init, reset, and polling. Atomic enable uses a custom helper that updates PIXPLLC, computes hiprilvl, loads gamma, and enables display.

## State and persistence
`struct mgag200_g200se_device` persists `unique_rev_id`. Device info captures revision-specific max display, bandwidth, DDC bits, and `bug_no_startadd`. CRTC state carries PLL and format. Hardware state includes PCI options, DAC PLL registers, ECRT hiprilvl, and BMC-related mode reset flags.

## Dependencies and integration points
Uses shared mgag200 KMS, mode, DDC, and BMC VGA helpers. Dispatched for G200_SE_A and G200_SE_B PCI IDs.

## Risks
Revision selection is central; a zero or unexpected unique ID aborts probe or may choose conservative limits. Older revision A info sets `bug_no_startadd`, forcing start address zero. PLL algorithms differ significantly, and rev04 update uses a DAC 0x1a toggle plus sleep sequence. Hiprilvl thresholds affect display stability under memory pressure.

## Test signals
Test each known SE revision class, A and B PCI IDs, maximum mode validation, hiprilvl behavior at multiple bpp/clocks, BMC/no-EDID fallback modes, and start-address warnings on affected revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200se.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200wb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200wb.c

## Purpose
Implements G200WB support, including WB register defaults, 48 MHz reference PLL search/programming, BMC-synchronized device info, pipeline creation, and factory setup.

## Important APIs, types, and functions
- `mgag200_g200wb_init_registers()` writes WB DAC defaults and shared VGA registers; reused by EW3.
- `mgag200_g200wb_pixpllc_atomic_check()` searches m/n/p for a 150-550 MHz VCO.
- `mgag200_g200wb_pixpllc_atomic_update()` performs a retry loop that disables clocks, selects PLL set C, resets VREF, writes WB PLL registers, selects PLL for pixel/remote head, and polls vertical count for lock.
- `mgag200_g200wb_device_create()` creates the device with WB limits and BMC-aware output.

## Control flow
Factory setup writes PCI options, maps resources, initializes shared state with WB info/functions, writes registers, probes VRAM, configures KMS, creates primary plane/CRTC/VGA-BMC output, resets config, and starts polling. Atomic enable uses the common CRTC helper and WB PLL update.

## State and persistence
Device info limits max mode to 1280x1024, bandwidth 31877, and enables BMC synchronization. PLL values persist in CRTC state; lock retry state is local. Hardware remote-head clock and DAC PLL state persist after update.

## Dependencies and integration points
Exports init and PLL update for EW3. Uses shared KMS helpers and BMC VGA output.

## Risks
PLL update retries mutate CRTC register 0x1e on later attempts and does not report lock failure. BMC sync means modesets interact with remote console handshakes. The 1280x1024 cap must match hardware/BMC limitations.

## Test signals
WB hardware should validate 1280x1024 preferred paths, BMC scanout coordination, PLL lock under repeated modesets, EDID and no-EDID fallback, and remote-head clock restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_g200wb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_mode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_mode.c

## Purpose
Implements shared mgag200 KMS mode-setting: CRTC register programming, gamma LUT handling, primary shadow plane updates into VRAM, display enable/disable, mode validation, atomic CRTC state management, and DRM mode_config setup.

## Important APIs, types, and functions
- Gamma helpers `mgag200_crtc_fill_gamma()` and `mgag200_crtc_load_gamma()` program DAC palette entries for RGB565/RGB888/XRGB8888.
- Register programming helpers: `mgag200_init_registers()`, `mgag200_set_mode_regs()`, `mgag200_set_format_regs()`, `mgag200_enable_display()`.
- Plane helpers: `mgag200_primary_plane_helper_atomic_check/update/enable/disable()` and `mgag200_primary_plane_helper_get_scanout_buffer()`.
- CRTC helpers: `mgag200_crtc_helper_mode_valid()`, `mgag200_crtc_helper_atomic_check/flush/enable/disable()`, state reset/duplicate/destroy functions.
- `mgag200_mode_config_init()` initializes DRM mode_config and VRAM availability.

## Control flow
Atomic plane check enforces no scaling and marks the CRTC mode changed when the framebuffer format changes, then stores the format in mgag200 CRTC state. Plane update copies damaged rectangles from the shadow buffer into MMIO VRAM, sets scanout start address to zero, and updates pitch/offset registers. Plane enable/disable toggles sequencer screen-off with a delay.

CRTC atomic check verifies a primary plane, asks the chip-specific PIXPLLC checker to populate CRTC state when the mode changes, and validates gamma LUT size. Atomic enable programs format and timing registers, calls chip-specific PLL update, loads gamma, and enables display. Atomic flush updates gamma on color-management-only changes. Mode validation enforces chip-specific max dimensions, 8-pixel horizontal granularity, CRTC register limits, VRAM capacity, and optional memory bandwidth limits.

Mode config wraps atomic commit tail with `mdev->rmmio_lock` so concurrent DDC register use cannot interleave with modesetting.

## State and persistence
`mdev->vram_available` persists the probed VRAM limit. `mgag200_crtc_state` persists the active format, PLL values, and BMC reset flag across atomic duplicates. Hardware CRTC, sequencer, graphics, DAC, palette, start address, offset, and display-enable registers persist until later commits or shutdown.

## Dependencies and integration points
Depends on DRM atomic, GEM shadow plane, damage helper, framebuffer format helpers, color management, panic scanout buffer support, and `mgag200_ddc.h`/driver structures. Chip-specific files install these helpers into their plane and CRTC function tables.

## Risks
Hardware timing encoding is packed across VGA CRTC and extended registers; off-by-one or high-bit mistakes produce invalid sync. The driver always scans out from VRAM offset zero due to hardware and BMC quirks, so damage copying must keep VRAM current. MMIO VRAM writes through `drm_fb_memcpy()` can be performance-sensitive. Busy-wait display enable/disable lacks vblank IRQ integration. Bandwidth validation uses an approximation and maximum bpp, which can reject or accept borderline modes conservatively.

## Test signals
Atomic modeset tests, format changes among RGB565/RGB888/XRGB8888, gamma LUT set/reset, damage clipping, panic scanout buffer export, memory-size rejection, bandwidth rejection, horizontal granularity checks, and concurrent EDID reads during modeset are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_reg.h

## Purpose
Defines Matrox MGA/G200 register offsets and bit fields used by the mgag200 DRM driver.

## Important APIs, types, and functions
- Drawing, memory, interrupt, status, OPMODE, VGA sequencer/CRTC, extended CRTC, and PCI option register offsets.
- Bit fields for misc clock selection, sync polarity, sequencer reset/screen-off, CRTC protection/interrupts, CRTCEXT mode/start/offset bits, and PCI option SGRAM bit.
- DAC indirect register addresses for TVP3026 and MGA1064 families.
- MGA1064 pixel clock control, PLL, remote-head, GPIO, display, sync, and power register definitions.
- Variant-specific PLL register aliases for WB, EV, EH, and ER chips.

## Control flow
No runtime control flow. The macros are consumed by register access helpers and chip-specific mode/PLL/BMC/DDC code.

## State and persistence
No C state. The definitions identify hardware registers whose values persist after MMIO or DAC writes.

## Dependencies and integration points
Included by `mgag200_drv.h`, which wraps many of these offsets in read/write macros. It is the low-level register ABI for every mgag200 source file.

## Risks
Many definitions are inherited from older XFree86-era code and include registers unused by the current KMS path. Wrong offsets or bit masks can damage modesetting, PLL, DDC, or BMC behavior. Variant-specific PLL aliases are easy to mix up because register M/N ordering differs by chip.

## Test signals
Compile coverage catches only syntax. Runtime register tracing around PLL programming, sync polarity, CRTC timings, DAC GPIO, and display enable/disable is needed to validate these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_vga.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_vga.c

## Purpose
Initializes a standard VGA connector and DAC encoder for non-BMC mgag200 outputs.

## Important APIs, types, and functions
- Encoder funcs use `drm_encoder_cleanup`.
- Connector helper funcs use generic DDC mode probing and DDC-based detect.
- Connector funcs use atomic reset/duplicate/destroy and standard fill modes.
- `mgag200_vga_output_init()` creates encoder, DDC adapter, connector, polling, and encoder attachment.

## Control flow
Output init creates a DAC encoder, restricts it to the single CRTC, creates the DDC bit-bang adapter, initializes a VGA connector with DDC, adds helper funcs, enables connect/disconnect polling, and attaches connector to encoder.

## State and persistence
The encoder and connector are embedded in `mdev->output.vga` and persist for the DRM device lifetime. The DDC adapter is DRM-managed.

## Dependencies and integration points
Used by original G200 PCI/AGP pipeline initialization. Depends on DRM connector/encoder helpers and `mgag200_ddc_create()`.

## Risks
Unlike the BMC-aware path, no fallback connected status or no-EDID modes are added. Systems without EDID may appear disconnected.

## Test signals
EDID detection, hotplug polling, connector mode listing, and successful encoder attachment on original G200 hardware are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_vga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_vga_bmc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_vga_bmc.c

## Purpose
Initializes a VGA connector/encoder path for server G200 variants where a BMC may be present even without a monitor or EDID.

## Important APIs, types, and functions
- Encoder atomic helpers call `mgag200_bmc_stop_scanout()` and `mgag200_bmc_start_scanout()` when `sync_bmc` is set.
- Encoder atomic check stores `set_vidrst` in `mgag200_crtc_state`.
- Connector get_modes falls back to no-EDID modes and prefers 1024x768.
- Connector detect always returns connected while updating `epoch_counter` when EDID presence changes.
- `mgag200_vga_bmc_output_init()` creates the encoder, DDC bus, connector, polling, and attachment.

## Control flow
During atomic check, the encoder records whether CRTC mode programming should set video reset bits. During disable/enable, BMC scanout is stopped/started only for variants whose device info requests synchronization. Mode probing first uses DDC; if no EDID modes exist, it adds bounded no-EDID modes up to the chip max and marks 1024x768 preferred.

## State and persistence
Connector and encoder live in `mdev->output.vga`. `connector->epoch_counter` is incremented on EDID presence changes to refresh properties. BMC sync state persists in DAC GPIO/spare registers via `mgag200_bmc.c` during modesets.

## Dependencies and integration points
Used by most server G200 variant pipeline initializers. Integrates with mgag200 DDC, BMC handshake helpers, and shared mode register programming through `set_vidrst`.

## Risks
Always reporting connected is correct for BMC console availability but can surprise userspace expecting physical monitor status. Fallback modes depend on max_hdisplay/max_vdisplay being conservative. BMC synchronization adds hardware-protocol timing risk.

## Test signals
No-monitor boot should still expose a connected VGA connector with 1024x768 preferred. EDID attach/detach should update properties. BMC remote console should survive modesets on `sync_bmc` variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_vga_bmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/Kconfig

## Purpose
Defines build-time configuration for the Qualcomm MSM/Snapdragon DRM driver, including core GPU support, KMS display blocks, DisplayPort, DSI PHY variants, HDMI, HDCP, debug-oriented GPU state, and developer-only options.

## Important APIs, types, and functions
- `DRM_MSM` is the root tristate depending on DRM, OF, PM, IOMMU support, common clocks, and Qualcomm optional subsystems, and selecting GPUVM/scheduler/exec/shmem/tmpfs/SCM/UBWC and other helpers.
- `DRM_MSM_GPU_STATE`, `DRM_MSM_GPU_SUDO`, and `DRM_MSM_VALIDATE_XML` configure diagnostics, privileged submit behavior, and XML schema validation.
- `DRM_MSM_KMS`, `DRM_MSM_KMS_FBDEV`, and `DRM_MSM_MDSS` provide display core selections.
- `DRM_MSM_MDP4`, `DRM_MSM_MDP5`, and `DRM_MSM_DPU` enable display controller generations.
- `DRM_MSM_DP`, `DRM_MSM_DSI`, DSI PHY options, `DRM_MSM_HDMI`, and `DRM_MSM_HDMI_HDCP` gate external display blocks.

## Control flow
This file is build-time Kconfig control flow. Selecting display controller or connector options pulls in KMS and required DRM display helpers. DSI and DP options gate include paths and object lists in the Makefile.

## State and persistence
No runtime state. Configuration choices persist in the kernel build and determine which objects, generated headers, and feature paths are compiled.

## Dependencies and integration points
Integrates MSM DRM with DRM core, scheduler, GPUVM, display helpers, panel/bridge helpers, MIPI DSI, DisplayPort AUX/helper code, HDMI helpers, power domains, OPP, NVMEM, and Qualcomm firmware/platform services.

## Risks
The root driver has broad dependency/select impact. `DRM_MSM_GPU_SUDO` intentionally grants CAP_SYS_RAWIO users kernel-level GPU command capability and is unsafe for production. XML validation depends on Python/lxml availability. Default-y display options can increase build surface.

## Test signals
Kconfig dependency resolution across ARCH_QCOM, COMPILE_TEST, and non-Qualcomm builds; minimal GPU-only builds; all display combinations; and validation of developer-only options are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/Makefile

## Purpose
Defines the MSM DRM build graph, including include paths, Adreno GPU objects, optional display-controller/output objects, generated register headers, and XML-to-C header generation rules.

## Important APIs, types, and functions
- `ccflags-y` adds source, generated, DPU, DSI, and DP include paths as needed.
- `adreno-y` lists core Adreno files from a2xx through a8xx, with optional debugfs and GPU state objects.
- `msm-display-*` object groups are gated by HDMI, MDP4, MDP5, DPU, MDSS, KMS, DP, HDMI HDCP, DSI, and DSI PHY configs.
- `msm-y` lists core GEM, GPU, fence, submit, syncobj, perf, IOMMU, trace, and KMS objects.
- Header generation rules invoke `registers/gen_header.py` for Adreno and display XML files, optionally with schema validation.
- `ADRENO_HEADERS` and `DISPLAY_HEADERS` define generated header dependencies for GPU and display objects.

## Control flow
Kbuild accumulates object lists based on Kconfig symbols, appends display objects into `msm-y` when KMS is enabled, links `msm.o` under `CONFIG_DRM_MSM`, and ensures relevant generated XML headers exist before compiling dependent objects. The `CONFIG_DRM_MSM_VALIDATE_XML` branch toggles generator validation flags.

## State and persistence
No runtime state. Generated headers under `$(obj)/generated` are build artifacts derived from XML register descriptions.

## Dependencies and integration points
Couples Kconfig selections to source compilation and generated register headers. Integrates with Python, rules-fd XML schema, freedreno register XMLs, and all MSM DRM subdirectories.

## Risks
Missing generated header dependencies can cause parallel build races. Include path changes can mask source/generated header mismatches. Object list omissions can break feature configs or leave Kconfig-enabled code unlinked. Validation depends on host Python/lxml support.

## Test signals
Build matrix coverage for GPU-only, KMS, HDMI, DP, DSI, DPU/MDP4/MDP5, debugfs, GPU state, and XML validation configs. Parallel builds are important to catch generated-header ordering issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_catalog.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_catalog.c

## Purpose
Registers catalog metadata for Adreno A2xx GPUs supported by the MSM DRM Adreno driver.

## Important APIs, types, and functions
- Static `a2xx_gpus[]` contains `struct adreno_info` entries for A200, i.MX51 A200 variant, A220, and A225.
- Each entry specifies chip IDs, family, revision number, firmware filenames, GMEM size, inactive period, and `a2xx_gpu_funcs`.
- `DECLARE_ADRENO_GPULIST(a2xx)` exports the catalog list to the Adreno device matching framework.

## Control flow
No executable control flow beyond static registration. At runtime, Adreno device matching scans declared GPU lists, matches chip IDs, loads the listed PM4/PFP firmware, and binds the A2xx function table.

## State and persistence
The catalog is static read-only driver data. Matched firmware names and GMEM sizes become part of runtime GPU device initialization state elsewhere.

## Dependencies and integration points
Depends on `adreno_gpu.h` for `struct adreno_info` and list declaration macros, and `a2xx_gpu.h` for `a2xx_gpu_funcs`. Firmware names must match linux-firmware or platform-provided firmware.

## Risks
Incorrect chip IDs can bind the wrong GPU generation. Firmware filenames are hardware-specific; A225 explicitly notes support only for msm8960v3 because v2 needed special firmware. Wrong GMEM size affects command submission and rendering correctness.

## Test signals
Probe logs for A200/A220/A225, successful firmware loading, correct GMEM size exposure, GPU idle timeout behavior, and rendering tests on the i.MX51 128 KiB GMEM variant are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_catalog.c -->

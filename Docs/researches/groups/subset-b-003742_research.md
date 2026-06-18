# subset-b-003742 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_plane.c

## Purpose
Implements SH Mobile DRM plane objects for the Renesas shmobile LCDC driver. It creates DRM primary and overlay planes, validates atomic plane state, computes DMA scanout addresses for RGB and semi-planar YUV framebuffers, and programs LCDC primary/overlay registers through the register helpers in `shmob_drm_regs.h`.

## Important APIs, Types, And Functions
The private `struct shmob_drm_plane` embeds `struct drm_plane` plus a hardware plane index. `struct shmob_drm_plane_state` extends `drm_plane_state` with resolved `shmob_drm_format_info` and up to two DMA base addresses. `shmob_drm_plane_create()` is the exported constructor. Atomic hooks are `shmob_drm_plane_atomic_check()`, `shmob_drm_plane_atomic_update()`, `shmob_drm_plane_atomic_disable()`, plus custom reset/duplicate/destroy state functions.

## Control Flow
Plane creation allocates a universal plane with supported formats and attaches helper funcs. Atomic check clears invisible/disabled state, fetches the CRTC state, rejects scaling through `drm_atomic_helper_check_plane_state()`, resolves the SH Mobile format descriptor, and precomputes DMA bases. Atomic update programs either primary registers (`LDDFR`, `LDMLSR`, `LDDDSR`, `LDSA*R`, `LDRCNTR`) or overlay registers (`LDBn*`) depending on plane type. Overlay disable clears `LDBnBSIFR` and triggers bank update bits.

## State And Persistence
Persistent driver state is the plane object, its index, and the custom plane state allocated during reset. Hardware state is written directly to memory-mapped LCDC registers at commit time. DMA addresses are recomputed per atomic state and not persisted outside `shmob_drm_plane_state`.

## Dependencies And Integration Points
Depends on DRM atomic helpers, DMA framebuffer helpers, GEM DMA objects, `shmob_drm_format_info()`, and LCDC register helpers. Primary planes expose `get_scanout_buffer = drm_fb_dma_get_scanout_buffer`, integrating with DRM scanout buffer queries.

## Risks
YUV colorimetry is hardcoded to REC709. Scaling is forbidden. DMA address calculation assumes the fb plane layout and YUV subsampling rules match the local format table. Overlay alpha uses `state->alpha >> 8`; blend semantics depend on LCDC register interpretation.

## Test Signals
Useful signals include atomic plane format rejection, no-scaling rejection, primary RGB/YUV scanout, overlay enable/disable register traces, plane alpha behavior, and framebuffer offsets/pitches for cropped planes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_plane.h

## Purpose
Declares the SH Mobile DRM plane creation interface used by the broader shmobile KMS setup.

## Important APIs, Types, And Functions
Forward declares `struct drm_plane` and `struct shmob_drm_device`, then exports `shmob_drm_plane_create(struct shmob_drm_device *sdev, enum drm_plane_type type, unsigned int index)`.

## Control Flow
This header has no runtime control flow. It provides the constructor contract for code that needs to instantiate primary or overlay planes.

## State And Persistence
No state is stored here. State ownership lives in the implementation file and DRM plane core.

## Dependencies And Integration Points
The prototype depends on DRM's `enum drm_plane_type` being visible to includers. It connects shmobile KMS initialization with the plane implementation.

## Risks
The header does not include a DRM header for `enum drm_plane_type`; includers must already have a suitable DRM declaration. Misordered includes could expose compile failures.

## Test Signals
Build coverage is the primary signal. A successful shmobile KMS build and plane creation path validates this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_regs.h

## Purpose
Defines SH Mobile LCDC register offsets, bit fields, banked/mirrored register behavior, and small MMIO helper functions used by the shmobile DRM driver.

## Important APIs, Types, And Functions
The file is mostly macro definitions for clock, timing, frame format, DMA base, interrupt/status, display control, overlay blend, and bank update registers. Helper functions include `lcdc_is_banked()`, `lcdc_write_mirror()`, `lcdc_write()`, `lcdc_read()`, and `lcdc_wait_bit()`.

## Control Flow
`lcdc_write()` writes the selected register and mirrors writes to the side-B bank when `lcdc_is_banked()` returns true. `lcdc_wait_bit()` polls a masked register field until it equals the expected value or a 5 ms jiffies timeout expires.

## State And Persistence
The header does not own software state. It codifies hardware state layout and write semantics. Register writes persist in the LCDC hardware until overwritten or reset.

## Dependencies And Integration Points
Depends on Linux MMIO APIs, jiffies/time helpers, and `struct shmob_drm_device` carrying `mmio`. Plane and CRTC code use these macros to program display timings, DMA addresses, formats, and overlay banks.

## Risks
Register constants are hardware-contract critical; wrong masks or banking classification can update only one side or corrupt unrelated fields. `lcdc_wait_bit()` busy-waits with `cpu_relax()` and no sleep, so it should remain limited to short hardware waits.

## Test Signals
Signals include successful LCDC enable/disable, primary and overlay register programming on both banks, timeout behavior for stuck status bits, and regression tests or hardware traces around mirrored DMA address writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/Kconfig

## Purpose
Defines build-time configuration for the Rockchip DRM driver and its optional display pipeline/output subdrivers.

## Important APIs, Types, And Functions
The top-level `DRM_ROCKCHIP` tristate depends on DRM, OF, Rockchip architecture or compile test, and selects common DRM helpers. Child bool options enable VOP, VOP2, Analogix DP, Cadence DP, Synopsys DW DP, DW HDMI, DW HDMI QP, DW MIPI DSI, DW MIPI DSI2, Innosilicon HDMI, LVDS, RGB, and RK3066 HDMI.

## Control Flow
Kconfig selection controls which platform drivers are compiled into the single `rockchipdrm` object and which helper libraries are selected. Conditional selects pull bridge, panel, DP, HDMI, MIPI, audio codec, and PHY support.

## State And Persistence
No runtime state. Configuration persists in the kernel build `.config` and directly changes object composition and probe-time subdriver registration.

## Dependencies And Integration Points
Integrates with DRM, bridge/helper libraries, extcon for Cadence DP, generic PHY for DSI, and SoC pinctrl requirements for LVDS/RGB. The selected symbols are consumed by `Makefile` and `rockchip_drm_drv.c`.

## Risks
Because many subdrivers are bool under a tristate parent, dependency mismatches can create missing symbol or unusable runtime combinations. Conditional `select` statements hide some dependencies, so adding a new bridge needs both Kconfig and Makefile updates.

## Test Signals
Build matrix coverage for built-in, module, COMPILE_TEST, and partial-output configurations is the main signal. Runtime probe coverage should confirm only enabled subdrivers are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/Makefile

## Purpose
Builds the Rockchip DRM composite object and conditionally includes each display controller/output implementation according to Kconfig.

## Important APIs, Types, And Functions
Defines `rockchipdrm-y` with the core driver, framebuffer, and GEM files. Appends controller/output objects through `rockchipdrm-$(CONFIG_...)` lines, then emits `obj-$(CONFIG_DRM_ROCKCHIP) += rockchipdrm.o`.

## Control Flow
No runtime control flow. Build control determines which C files contribute platform driver symbols referenced by the top-level registration table.

## State And Persistence
No runtime state. The built object composition persists in the kernel build output.

## Dependencies And Integration Points
Must stay synchronized with `Kconfig` and `rockchip_drm_drv.c` `ADD_ROCKCHIP_SUB_DRIVER()` calls. For Cadence DP, both `cdn-dp-core.o` and `cdn-dp-reg.o` are included together.

## Risks
Missing an object for a Kconfig symbol produces undefined references when the core tries to register that subdriver. Adding an object without a matching Kconfig path can produce dead code or unexpected build growth.

## Test Signals
Compile tests across all optional symbols, especially `allyesconfig`, `allmodconfig`, and minimal configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/analogix_dp-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/analogix_dp-rockchip.c

## Purpose
Provides Rockchip-specific glue for the Analogix DisplayPort/eDP core. It handles GRF muxing, clocks, resets, panel/AUX discovery, runtime PM, encoder setup, and SoC-specific chip data for RK3288, RK3399, and RK3588 eDP/DP blocks.

## Important APIs, Types, And Functions
Key structs are `rockchip_grf_reg_field`, `rockchip_dp_chip_data`, and `rockchip_dp_device`. Core callbacks include `rockchip_dp_poweron()`, `rockchip_dp_powerdown()`, `rockchip_dp_get_modes()`, encoder helpers, `rockchip_dp_bind()`, `rockchip_dp_link_panel()`, `rockchip_dp_probe()`, and PM callbacks.

## Control Flow
Probe matches SoC data by compatible and MMIO resource start, obtains GRF, clocks, and resets, then calls `analogix_dp_probe()`. AUX bus population eventually calls `rockchip_dp_link_panel()` and registers the component. Bind creates the DRM encoder, sets endpoint IDs, and delegates to `analogix_dp_bind()`. Atomic enable chooses the active VOP endpoint and writes LCDC selection to GRF; disable waits for vertical active end when entering self refresh.

## State And Persistence
The device stores clock/reset/regmap handles, selected chip data, Analogix core handle, and DRM mode. GRF writes persist SoC mux and eDP mode state. Runtime PM delegates suspend/resume to the Analogix core.

## Dependencies And Integration Points
Depends on Analogix DP bridge APIs, DP AUX bus population, DRM OF graph helpers, Rockchip encoder endpoint metadata, reset/clock/regmap frameworks, and optional panel/bridge nodes.

## Risks
The RK3588 chip-data selection relies on MMIO base addresses. Some enable paths return without disabling `grfclk` if endpoint lookup fails. Color formats are forced from YUV to RGB due to VOP limitations, which may surprise sinks.

## Test Signals
Probe on each compatible, panel and driver-free DP mode, AUX bus population with and without panel endpoints, runtime suspend/resume, self-refresh transitions, and GRF mux correctness for big/little VOP endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/analogix_dp-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-core.c

## Purpose
Implements the Rockchip RK3399 Cadence DisplayPort bridge driver. It manages firmware loading, Type-C/extcon port selection, PHY power, link training, EDID/DPCD access, video and audio bridge operations, HPD notification, suspend/resume, and component binding to Rockchip DRM.

## Important APIs, Types, And Functions
Uses `struct cdn_dp_device`, `struct cdn_dp_port`, and `struct cdn_dp_data`. Major functions include `cdn_dp_enable()`, `cdn_dp_disable()`, `cdn_dp_bridge_atomic_enable()`, `cdn_dp_bridge_atomic_disable()`, `cdn_dp_pd_event_work()`, `cdn_dp_bind()`, `cdn_dp_probe()`, audio callbacks, and firmware helpers. It delegates register/mailbox operations to `cdn-dp-reg.c`.

## Control Flow
Probe discovers extcon/PHY pairs and registers a component. Bind parses DT resources, initializes encoder/bridge/connector, registers extcon notifiers, enables runtime PM, and schedules event work. Event work requests firmware, checks connected ports, powers PHY, reads sink DPCD, enables the controller, and notifies bridge HPD. Atomic enable selects VOP in GRF, enables DP, validates or trains the link, idles video, configures video, then marks video valid.

## State And Persistence
State is protected by `dp->lock` and includes `connected`, `active`, `suspended`, firmware state, active port, lane/rate results, DPCD cache, audio/video info, and per-port `phy_enabled`. Firmware is cached until unbind; hardware state is reset on enable/disable and suspend.

## Dependencies And Integration Points
Integrates with DRM bridge connector, Rockchip encoder atomic state, extcon Type-C properties, PHY framework, syscon GRF, clocks/resets, runtime PM, firmware loader, and HDMI codec bridge audio callbacks.

## Risks
Firmware load can block/retry for up to 64 seconds. Hotplug state is asynchronous and depends on extcon plus DPCD reads. Error paths in link enable must keep PHY, HPD mux, clocks, and firmware active state balanced. Mode validation assumes 80% DP efficiency and uses cached DPCD.

## Test Signals
Firmware missing/delayed load, Type-C orientation and lane-count changes, dock-without-sink cases, retraining after link-status failure, audio I2S/SPDIF prepare/mute/shutdown, suspend/resume with active display, and HPD userspace notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-core.h

## Purpose
Defines shared Cadence DP core data structures used by the Rockchip Cadence DP bridge and mailbox/register implementation.

## Important APIs, Types, And Functions
Declares `MAX_PHY`, `enum audio_format`, `struct audio_info`, video pixel encoding enum, `struct video_info`, `struct cdn_firmware_header`, `struct cdn_dp_port`, and `struct cdn_dp_device`.

## Control Flow
No executable control flow. It shapes how `cdn-dp-core.c` and `cdn-dp-reg.c` share device, firmware, audio, video, DPCD, and port state.

## State And Persistence
`struct cdn_dp_device` is the main persistent runtime state object, holding DRM objects, work item, mutex, connection flags, firmware pointer/version, MMIO/regmap/clock/reset handles, audio/video state, port list, negotiated link parameters, active port, and DPCD buffer.

## Dependencies And Integration Points
Includes DRM DP, bridge, panel/probe helpers, HDMI codec, and Rockchip DRM driver types. The header is the contract between DP policy code and low-level mailbox programming.

## Risks
The maximum port count is fixed at two. Shared mutable fields such as `max_lanes`, `max_rate`, and `active_port` require external locking discipline; the header itself cannot enforce it.

## Test Signals
Compile coverage of both Cadence DP source files and runtime tests that exercise all fields: multi-port extcon, firmware load, link training, audio, and DPCD reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-reg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-reg.c

## Purpose
Implements low-level Cadence DP firmware, mailbox, DPCD, link-training, video, and audio register operations used by `cdn-dp-core.c`.

## Important APIs, Types, And Functions
Public functions include `cdn_dp_set_fw_clk()`, `cdn_dp_clock_reset()`, `cdn_dp_load_firmware()`, `cdn_dp_set_firmware_active()`, `cdn_dp_set_host_cap()`, `cdn_dp_event_config()`, `cdn_dp_get_event()`, `cdn_dp_get_hpd_status()`, DPCD read/write, EDID block read, `cdn_dp_train_link()`, `cdn_dp_config_video()`, and audio config/stop/mute helpers. Internal mailbox helpers serialize commands to the firmware.

## Control Flow
Clock reset enables source, PHY, AUX, packet, audio, cipher, and crypto clocks. Firmware load writes IRAM/DRAM, releases reset, polls keep-alive, and records firmware version. Mailbox commands write headers and payload bytes, validate reply headers, and drain mismatched replies. Link training starts firmware training, polls training events, then reads negotiated link status. Video config computes TU/valid-symbol parameters and writes MSA/framer registers. Audio config programs I2S or SPDIF paths and enables audio packets.

## State And Persistence
Updates `dp->fw_version`, `dp->max_rate`, `dp->max_lanes`, and audio/video hardware registers. Most operations persist in the DP controller/firmware until disabled or reset.

## Dependencies And Integration Points
Depends on `cdn-dp-reg.h` register constants, firmware command IDs, DRM DP helpers, MMIO polling, and `struct cdn_dp_device` from `cdn-dp-core.h`.

## Risks
Mailbox timeouts are long and synchronous. The mailbox validation drains unexpected replies, so interleaved callers would be unsafe without the core lock. Audio sample rates/widths assume supported cases; unsupported values can leave `val` paths under-specified. TU calculation rejects modes only after iterative register math.

## Test Signals
Firmware keep-alive, mailbox timeout/reply mismatch, DPCD address validation, EDID block retries, link training event bits, high-bandwidth mode TU calculation, and I2S/SPDIF audio output at all advertised sample rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-reg.h

## Purpose
Defines Cadence DP register addresses, firmware mailbox protocol constants, bit fields, enums, and function prototypes for the Cadence DP register library.

## Important APIs, Types, And Functions
The header covers APB, mailbox, source, PHY, HPD, framer, AUX, HDCP, audio, and stream registers. It defines mailbox module/opcode IDs, firmware states, event bits, link-training bits, video/audio constants, DP lane mapping, link-rate limit, and enums for voltage swing, pre-emphasis, pattern set, color depth, and BT type. Public prototypes match `cdn-dp-reg.c`.

## Control Flow
No runtime control flow. The macros parameterize mailbox commands and MMIO writes in `cdn-dp-reg.c`.

## State And Persistence
No software state is stored. Constants describe persistent hardware/firmware state fields and command payload encodings.

## Dependencies And Integration Points
Includes Linux bitops and references `struct cdn_dp_device`, `struct audio_info`, and video data defined in `cdn-dp-core.h`. It is the shared ABI between the core driver and low-level DP firmware interface.

## Risks
Typos or stale constants can break firmware communication silently. `CDN_DP_MAX_LINK_RATE` caps the source at HBR2 despite possible sink capabilities. Protocol constants are not self-validating and rely on matching the firmware binary.

## Test Signals
Compile coverage and hardware smoke tests for firmware activation, DPCD/EDID reads, link training, video enable, and audio packet programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw-mipi-dsi-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw-mipi-dsi-rockchip.c

## Purpose
Provides Rockchip glue for Synopsys DesignWare MIPI DSI host controllers and also exposes some controllers as MIPI DPHY providers. It configures SoC GRF lane/mux registers, internal/external PHY timing, dual-DSI operation, DRM encoder state, and component binding.

## Important APIs, Types, And Functions
Key structs are `rockchip_dw_dsi_chip_data`, `dw_mipi_dsi_rockchip`, `dphy_pll_parameter_map`, and `hstt`. Major flows include `dw_mipi_dsi_get_lane_mbps()`, `dw_mipi_dsi_phy_init()`, `dw_mipi_dsi_rockchip_bind()`, host attach/detach, exported DPHY ops, resume reconfiguration, and the SoC chip-data tables for PX30, RK3128, RK3288, RK3368, RK3399, RK3506, RK3568, and RV1126.

## Control Flow
Probe maps registers, selects chip data by MMIO base, gets clocks, optional external DPHY, GRF, creates a PHY provider, and probes the DW DSI core. Host attach claims usage mode and registers one or two components. Bind resolves dual-DSI clock master/slave, enables runtime PM and PLL reference clock, writes static GRF lane config, creates encoder, sets endpoint ID, and binds the DW DSI core. Atomic check translates DSI pixel format into Rockchip output mode and marks dual DSI when a slave is present.

## State And Persistence
Persistent state includes usage mode under `usage_mutex`, dual-channel pointers, lane Mbps, PLL divisors, pixel format, PHY config, bound state, and chip data. GRF and PHY test-interface writes persist until reset or resume reprogramming.

## Dependencies And Integration Points
Integrates with `drm/bridge/dw_mipi_dsi`, MIPI DSI host attach, generic PHY/DPHY framework, runtime PM, syscon GRF, DRM OF graph, and Rockchip VOP output state.

## Risks
Dual-DSI discovery peeks at peer driver data and forces synchronous probe. Usage-mode arbitration must prevent simultaneous DSI-host and DPHY-provider use. PLL parameter calculations are sensitive to reference clock and lane rate. Several GRF constants come from BSP or undocumented registers.

## Test Signals
Single and dual DSI panels, clock-master validation, external versus internal DPHY paths, exported DPHY receiver mode on RK3399, suspend/resume before panel enable, RGB565/666/888 output modes, and probe ordering with peer DSI nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw-mipi-dsi-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw-mipi-dsi2-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw-mipi-dsi2-rockchip.c

## Purpose
Implements Rockchip glue for the newer DesignWare MIPI DSI2 host, targeting RK3576 and RK3588 DSI2/DCPHY style controllers.

## Important APIs, Types, And Functions
Defines GRF field metadata through `struct dsigrf_reg` and `enum grf_reg_fields`, SoC data in `rockchip_dw_dsi2_chip_data`, and runtime state in `dw_mipi_dsi2_rockchip`. Major callbacks are DSI2 PHY ops, encoder atomic enable/check, host attach/detach, component bind/unbind, and probe/remove.

## Control Flow
Probe maps the host register block into a regmap, chooses chip data by MMIO base, obtains GRF and optional DCPHY, fills `dw_mipi_dsi2_plat_data`, and probes the DW DSI2 core. Host attach registers the component. Bind creates the DRM encoder, records endpoint ID, and binds the DSI2 core. Lane Mbps is calculated from pixel clock, bpp, lanes, and optional burst overhead, then converted into external PHY options. Atomic enable writes IPI color depth to GRF; atomic check fills Rockchip CRTC output mode, bus format, flags, and color space.

## State And Persistence
Stores selected format, lane Mbps, external PHY options, GRF data, and DW DSI2 core handle. GRF field writes persist IPI color-depth state for the hardware.

## Dependencies And Integration Points
Depends on `drm/bridge/dw_mipi_dsi2`, generic PHY MIPI DPHY config, syscon GRF, DRM OF helpers, media bus formats, and Rockchip CRTC state.

## Risks
`grf_field_write()` assumes the chip data has a valid `grf_regs` array for every enum field. Lane-rate units must stay consistent with the SoC max-bit-rate values. Only DPHY is exposed; CPHY/other DCPHY modes are not handled here.

## Test Signals
RK3576 and RK3588 probe by base address, external DCPHY configure/power, burst and non-burst lane-rate checks, RGB565/666/888 formats, and GRF color-depth programming during atomic enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw-mipi-dsi2-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_dp-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_dp-rockchip.c

## Purpose
Provides Rockchip glue for Synopsys DesignWare DisplayPort controllers on RK3576 and RK3588.

## Important APIs, Types, And Functions
Defines `struct rockchip_dw_dp`, the encoder atomic check callback, component bind ops, platform probe/remove, and per-SoC `dw_dp_plat_data` entries for maximum link rate and pixel mode.

## Control Flow
Probe registers a component. Bind allocates runtime state, finds platform data from DT match, creates a DRM encoder, records CRTC endpoint ID, binds the DW DP bridge core, creates a bridge connector, and attaches the connector to the encoder. Atomic check reads the first bridge input bus format and maps it to Rockchip output mode, bus format, bus flags, and color space.

## State And Persistence
State is small: the DW DP core handle, device pointer, and embedded Rockchip encoder. Hardware persistence is delegated to the DW DP bridge core.

## Dependencies And Integration Points
Integrates with `drm/bridge/dw_dp`, bridge connector helpers, media bus format definitions, V4L2 color space constants, DRM OF graph, and Rockchip encoder endpoint metadata.

## Risks
Atomic check expects bridge state and first bridge to exist. Unsupported bus formats fall back to `ROCKCHIP_OUT_MODE_AAAA`, which may hide mismatches. Remove retrieves driver data that is only set during bind, so lifecycle ordering depends on component behavior.

## Test Signals
RK3576/RK3588 probe, connector creation, each supported RGB/YUV bus format, endpoint ID mapping, and bridge-state availability during atomic check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_dp-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_hdmi-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_hdmi-rockchip.c

## Purpose
Implements Rockchip-specific glue for the Synopsys DW HDMI bridge on RK3228, RK3288, RK3328, RK3368, RK3399, and RK3568.

## Important APIs, Types, And Functions
Uses `rockchip_hdmi_chip_data` and `rockchip_hdmi`. Important callbacks include DT parsing, mode validation, encoder mode-set/enable/atomic-check, generic PHY init/disable, RK3228/RK3328 HPD setup/read, component bind/unbind, and resume.

## Control Flow
Bind copies SoC platform data, sets Rockchip private data into DW HDMI platform data, finds possible CRTCs, parses GRF/clocks/regulators, gets optional HDMI PHY and PHY clock, applies RK3568 SDA/SCL masks, initializes encoder, and calls `dw_hdmi_bind()`. Encoder mode_set programs the reference clock to adjusted pixel clock. Encoder enable writes GRF LCDC/VOP mux for SoCs that need it. Mode validation checks max TMDS clock and whether ref/PHY clocks can round within 0.1%.

## State And Persistence
Stores GRF regmap, encoder, chip/platform data, ref/grf/hdmiphy clocks, optional PHY, and DW HDMI handle. GRF HPD voltage/mux and VOP mux writes persist in hardware.

## Dependencies And Integration Points
Depends on DW HDMI bridge APIs, DRM OF graph, syscon GRF, clock/regulator/PHY frameworks, Rockchip CRTC state, and HDMI infoframe support through DW HDMI platform data.

## Risks
Clock round-rate validation can reject modes on clock tree limitations. Some SoCs have special HPD voltage handling. Optional external PHY paths must balance `phy_power_on/off`. Bind manually cleans the encoder if `dw_hdmi_bind()` fails.

## Test Signals
Probe and modeset on every compatible, HPD voltage behavior on RK3228/RK3328, max TMDS enforcement, 594 MHz modes where supported, GRF VOP selection on RK3288/RK3399, regulator failures, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_hdmi-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_hdmi_qp-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_hdmi_qp-rockchip.c

## Purpose
Provides Rockchip glue for DW HDMI QP controllers on RK3576 and RK3588, including HDMI 2.1-style PHY configuration, HPD interrupt handling, GRF/VO-GRF IO setup, and bridge connector integration.

## Important APIs, Types, And Functions
Key types are `rockchip_hdmi_qp`, `rockchip_hdmi_qp_ctrl_ops`, and `rockchip_hdmi_qp_cfg`. Important callbacks cover encoder enable/atomic-check, PHY power, HPD read/setup, hard IRQ/threaded IRQ, delayed HPD work, SoC IO init, encoder color-depth init, component bind/unbind, and PM suspend/resume.

## Control Flow
Bind identifies the HDMI port by MMIO base, obtains GRF and VO-GRF regmaps, enables all clocks, reads ref clock rate, gets optional FRL GPIO and required PHY, runs SoC IO init, registers threaded HPD IRQ, creates encoder, binds DW HDMI QP, initializes bridge connector, and attaches it. Atomic check configures the HDMI PHY when TMDS character rate or bpc changes and updates Rockchip CRTC output state. Enable forces TMDS by clearing FRL GPIO and writes color-depth state. HPD IRQ masks, clears, debounces, and notifies DRM.

## State And Persistence
Stores selected port, cached TMDS character rate, encoder, PHY, HPD delayed work, GRF handles, and FRL GPIO. GRF/VO-GRF writes persist HPD, pin, grant, mode, and color-depth settings.

## Dependencies And Integration Points
Depends on DW HDMI QP bridge, DRM HDMI state helper data, bridge connector, generic HDMI PHY options, GPIO, clocks, IRQs, system workqueues, and Rockchip CRTC state.

## Risks
FRL is explicitly disabled even though QP hardware may support it. HPD status registers differ by SoC and port, so port base matching is critical. The cached `tmds_char_rate` avoids repeated PHY config but must stay coherent with bpc.

## Test Signals
RK3576/RK3588 port-ID matching, HPD IRQ debounce, PHY configure failures, 8/10 bpc modes, suspend/resume IO reinit and HPD event, FRL GPIO behavior, and dual-port RK3588 operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_hdmi_qp-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/inno_hdmi-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/inno_hdmi-rockchip.c

## Purpose
Adds Rockchip platform glue for Innosilicon HDMI controllers on RK3036 and RK3128.

## Important APIs, Types, And Functions
Defines RK3036/RK3128 PHY config tables, `rockchip_inno_hdmi`, `inno_hdmi_rk3036_enable()`, encoder atomic check, component bind/probe/remove, and SoC-specific `inno_hdmi_plat_data`.

## Control Flow
Probe registers a component. Bind allocates state, fetches SoC platform data, optionally obtains GRF for RK3036 sync polarity programming, creates a TMDS encoder, adds helper funcs, delegates controller setup to `inno_hdmi_bind()`, then creates and attaches a bridge connector. RK3036 enable writes HSYNC/VSYNC polarity into GRF based on the display mode.

## State And Persistence
Keeps the Inno HDMI core pointer, device, GRF regmap, and embedded encoder. GRF polarity writes persist in SoC registers.

## Dependencies And Integration Points
Depends on `drm/bridge/inno_hdmi`, DRM bridge connector, DRM OF graph helpers, syscon GRF, and Rockchip CRTC state.

## Risks
Only RK3036 uses GRF polarity enable ops; RK3128 relies entirely on the bridge core and PHY config table. The local `inno_hdmi_connector_state` is defined but unused, which may indicate historical leftovers.

## Test Signals
Probe on RK3036/RK3128, bridge connector creation, CRTC defer when possible CRTCs are absent, RK3036 sync polarity changes, and HDMI mode output as P888.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/inno_hdmi-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rk3066_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rk3066_hdmi.c

## Purpose
Implements a native Rockchip RK3066 HDMI bridge/encoder driver, including MMIO programming, DDC/EDID I2C adapter, HPD IRQ handling, bridge HDMI infoframe callbacks, video timing setup, and component integration.

## Important APIs, Types, And Functions
Key state types are `hdmi_data_info`, `rk3066_hdmi_i2c`, and `rk3066_hdmi`. Important functions include power-mode sequencing, I2C init/xfer/read/write, AVI infoframe write/clear, video timing setup, PHY config, bridge atomic enable/disable, detect/EDID/mode_valid, IRQ handlers, `rk3066_hdmi_register()`, and bind/unbind.

## Control Flow
Bind maps registers, requests IRQ, enables hclk, obtains GRF, initializes internal divider and interrupt masks, registers the DRM bridge/connector, then requests threaded IRQ. Atomic enable chooses VOP mux in GRF, configures HDMI video: mute, power mode B, RGB 8-bit input/output, timing registers, HDMI/DVI mode, infoframes, PHY magic values by TMDS clock, power mode E, DDC clock, and unmute video. Atomic disable mutes/reset audio/video and powers down to mode A. DDC transfers program EDID segment/word and wait for EDID completion IRQ.

## State And Persistence
Tracks current `tmdsclk`, HDMI colorimetry/VIC data, I2C DDC state, completion status, connector, bridge, encoder, GRF, hclk, and MMIO base. Hardware registers persist power, timing, PHY, interrupt, and infoframe state.

## Dependencies And Integration Points
Depends on DRM bridge connector and HDMI state helpers, I2C core, syscon GRF, clock framework, IRQ completions, and Rockchip CRTC state.

## Risks
PHY configuration uses undocumented magic values. The DDC adapter only supports EDID-style read sequences and returns `-EINVAL` for general writes. Mode validation only accepts CEA VIC > 1. HDMI Vendor Specific InfoFrame is stubbed with a warning.

## Test Signals
CEA mode validation, EDID reads across segment/address messages, HPD and MSENS IRQs, power-mode transition timing, VOP mux selection, AVI infoframe writes, high/medium/low TMDS PHY tables, and cleanup after IRQ or registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rk3066_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rk3066_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rk3066_hdmi.h

## Purpose
Defines RK3066 HDMI register offsets, DDC/audio constants, infoframe buffer constants, and bit-field values used by the native RK3066 HDMI driver.

## Important APIs, Types, And Functions
Contains macros for GRF video selection, DDC addresses/rates, audio N values, HDMI system/audio/video/DDC/interrupt/HDCP/status registers, and an enum of field masks/values for power modes, audio input, sample frequency, video format/depth, external timing, AV mute, infoframe selectors, interrupts, HDMI/DVI mode, and HPD/MSENS status.

## Control Flow
No executable control flow. Values are consumed by `rk3066_hdmi.c` MMIO helpers and bridge callbacks.

## State And Persistence
No software state. Constants describe persistent hardware register layout.

## Dependencies And Integration Points
Requires common bit macros from includers. It is tightly coupled to `rk3066_hdmi.c` and the RK3066 HDMI hardware block.

## Risks
The header includes many byte-sized register fields even though MMIO helpers use 32-bit relaxed reads/writes and cast to `u8`. Incorrect masks can silently affect adjacent hardware fields. Some undocumented PHY offsets are intentionally not named here and remain in the C file.

## Test Signals
Successful compile, DDC register programming, interrupt status/mask handling, power mode transitions, and video timing register writes on RK3066 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rk3066_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_drv.c

## Purpose
Implements the top-level Rockchip DRM platform driver. It registers optional subdrivers, matches display components, creates the DRM device, initializes mode config/GEM/IOMMU/vblank/polling, and coordinates bind/unbind/shutdown/suspend/resume for the display subsystem.

## Important APIs, Types, And Functions
Public helper APIs include `rockchip_drm_dma_attach_device()`, `rockchip_drm_dma_detach_device()`, `rockchip_drm_dma_init_device()`, `rockchip_drm_encoder_set_crtc_endpoint_id()`, and `rockchip_drm_endpoint_is_subdriver()`. Major internal functions include `rockchip_drm_bind()`, `rockchip_drm_unbind()`, IOMMU init/cleanup, component match construction, platform probe/remove/shutdown, and module init/fini.

## Control Flow
Module init builds the subdriver table according to enabled Kconfig symbols, registers them, then registers the master platform driver. Platform probe validates `ports`, builds a component match list with preferred VOP ordering and all registered subdriver devices, and registers the component master. Bind removes conflicting framebuffers, allocates DRM device/private data, initializes mode config, binds all subcomponents, initializes IOMMU, vblank and polling, registers DRM, and starts DRM clients. Unbind reverses registration, polling, atomic state, components, IOMMU, and DRM reference.

## State And Persistence
Persistent module state is `rockchip_sub_drivers[]` and count. Per-DRM private state includes IOMMU domain, aperture allocator, DMA device, and GEM address management. Device links are created during match construction and removed on teardown.

## Dependencies And Integration Points
Integrates with Linux component framework, OF graph, DRM core/client/fbdev/GEM DMA helpers, IOMMU and ARM DMA-IOMMU compatibility, aperture helpers, and all Rockchip subdriver platform symbols.

## Risks
`MAX_ROCKCHIP_SUB_DRIVERS` must cover every optional subdriver. Component matching treats platform devices with no bound Rockchip driver as external bridges, so probe ordering matters. IOMMU attachment detaches legacy ARM DMA mappings and assumes all display components share a domain.

## Test Signals
Builds across Kconfig combinations, display-subsystem DT validation, preferred VOP ordering, component bind failure unwinding, IOMMU and non-IOMMU systems, framebuffer handoff removal, suspend/resume, shutdown atomic disable, and endpoint subdriver detection for bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_drv.c -->

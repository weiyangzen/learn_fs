# Research: subset-b-003746

Grouped research for STMicroelectronics STI DRM display files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/sti`. Each section is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_compositor.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_compositor.c

Purpose: Implements the `sti-compositor` component driver that maps the compositor register bank, obtains compositor and pixel clocks, deasserts main/aux reset controls, resolves VTG phandles, and builds the in-DRM topology for the STiH407 compositor.

Important APIs/functions: `sti_compositor_probe()` allocates `struct sti_compositor`, loads `stih407_compositor_data`, maps registers, gets `compo_main`, `compo_aux`, `pix_main`, and `pix_aux` clocks, acquires `compo-main`/`compo-aux` resets, and registers component ops. `sti_compositor_bind()` stores `dev_priv->compo`, creates VID and mixer subdevices first, then creates cursor/GDP planes and initializes CRTCs with the first GDP planes as primaries. `sti_compositor_debugfs_init()` delegates debugfs setup to VID and mixer subdevices.

Control flow: Binding is intentionally two-pass. The first pass constructs mixers and VID blocks because planes and CRTCs depend on them. The second pass creates cursor/GDP planes from descriptor offsets and calls `sti_crtc_init()` while primary plane slots are available. `drm_vblank_init()` is sized to the number of created CRTCs.

State/persistence: Runtime state is held in the devm-managed `struct sti_compositor`, including register base, descriptor copy, clock/reset handles, mixer/VID/VTG arrays, and VTG notifier blocks initialized to `sti_crtc_vblank_cb`.

Dependencies/integration: Uses Linux component framework, OF matching for `st,stih407-compositor`, DRM core, reset/clock APIs, and STI local modules (`sti_crtc`, `sti_cursor`, `sti_gdp`, `sti_mixer`, `sti_vid`, `sti_vtg`). The compositor is the anchor referenced by `sti_private`.

Risks/test signals: Error paths usually abort probe on missing mandatory clocks/registers but component bind logs and continues past failed plane creation, which can leave fewer CRTCs/planes than expected. Test with device-tree clock/reset/phandle coverage, KMS plane enumeration, vblank init count, and debugfs mixer/VID files after CRTC late registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_compositor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_compositor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_compositor.h

Purpose: Defines the public compositor data structures shared by the STI DRM compositor, CRTC, mixer, GDP, VID, and VTG code.

Important APIs/types: `enum sti_compositor_subdev_type` classifies mixer, GDP, VID, and cursor subdevices. `struct sti_compositor_subdev_descriptor` records type, logical id, and register offset. `struct sti_compositor_data` carries the hardware descriptor table, bounded by `MAX_SUBDEV`. `struct sti_compositor` stores device context, register base, clocks, resets, mixer/VID/VTG pointers, and VTG vblank notifier blocks. `sti_compositor_debugfs_init()` is exported to CRTC late registration.

Control/state: The header makes the compositor the shared persistence object for display pipeline construction. `STI_MAX_MIXER` and `STI_MAX_VID` fix array bounds to two mixers and one VID for this generation. `WAIT_NEXT_VSYNC_MS` is a timing constant consumed by display synchronization code in this driver family.

Dependencies/integration: Includes kernel clock/reset-facing types and local `sti_mixer.h`/`sti_plane.h`. It is included by the compositor, CRTC, GDP, HQVDP, cursor, and VID paths to locate common resources.

Risks/test signals: Descriptor bounds must match platform data; adding hardware blocks requires keeping `MAX_SUBDEV`, array limits, and descriptor initialization consistent. Compile-time coverage and KMS enumeration are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_compositor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_crtc.c

Purpose: Implements DRM CRTC behavior for STI mixers. Each `struct sti_mixer` embeds the DRM CRTC and the CRTC code controls clocks, VTG timing, mixer active area, plane commit flushing, and vblank notification.

Important APIs/functions: `sti_crtc_init()` calls `drm_crtc_init_with_planes()` and installs helper funcs. `sti_crtc_mode_set()` enables the compositor path clock, sets pixel-clock rate from mode clock, programs VTG timing, and configures mixer active video area. `sti_crtc_atomic_flush()` processes STI plane status transitions, programs mixer depth/status, commits HQVDP-backed VID state, and arms pending vblank events. `sti_crtc_vblank_cb()` bridges VTG top/bottom field events into `drm_crtc_handle_vblank()` and completes synchronized mixer shutdown.

Control flow: Atomic enable marks the mixer ready and enables DRM vblank. Atomic disable marks the mixer disabling and waits one vblank; final clock/background shutdown is deferred until the VTG callback observes that overlay planes are disabled. Plane flush recognizes `STI_PLANE_UPDATED` and `STI_PLANE_DISABLING`, updating mixer registers and plane status.

State/persistence: Mixer status is the CRTC state machine (`READY`, `DISABLING`, `DISABLED`). Plane statuses are consumed here to coordinate asynchronous disabling. Vblank events are stored in DRM CRTC state and armed under `event_lock`.

Dependencies/integration: Depends on DRM atomic helpers, vblank API, common clocks, `sti_compositor`, `sti_mixer`, `sti_vid`, and VTG notifier registration. Debugfs setup for compositor subdevices happens in CRTC late registration for CRTC index 0.

Risks/test signals: Shutdown correctness depends on every non-cursor overlay eventually reaching `STI_PLANE_DISABLED`. Missing VTG events can leave clocks enabled or CRTC stuck disabling. Test with atomic enable/disable, page-flip event delivery, vblank on/off, plane disable races, and mixer debugfs state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_crtc.h

Purpose: Declares the CRTC-facing interface for mixer-backed STI CRTCs.

Important APIs: `sti_crtc_init()` creates a DRM CRTC around a mixer, primary plane, and cursor plane. `sti_crtc_vblank_cb()` is the VTG notifier callback installed by the compositor. `sti_crtc_is_main()` tells output encoders whether an encoder is driven by the main or auxiliary mixer path.

Control/state: The header deliberately hides mixer internals while exposing the small integration surface needed by compositor and TVOUT. The vblank callback signature follows the Linux notifier API and receives the DRM CRTC as callback data through VTG registration.

Dependencies/integration: Forward declares DRM and STI structs to avoid broad header coupling. It is used by compositor setup and by TVOUT encoder programming to choose main/aux sync routing.

Risks/test signals: Any change in mixer-to-CRTC embedding or notifier data must preserve these contracts. Compile and atomic modeset tests catch most integration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_cursor.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_cursor.c

Purpose: Implements the STI hardware cursor as a DRM universal cursor plane. Hardware accepts CLUT8 cursor data, so the driver exposes ARGB8888 and converts into a DMA pixmap plus generated CLUT.

Important APIs/functions: `sti_cursor_create()` allocates `struct sti_cursor`, allocates a 256-entry CLUT with `dma_alloc_wc()`, initializes the CLUT, registers a DRM cursor plane, and installs atomic helpers. `sti_cursor_atomic_check()` validates 1..128 source size, reallocates the pixmap when dimensions change, and verifies a DMA GEM object exists. `sti_cursor_atomic_update()` converts ARGB8888 to CLUT8, writes active-window, pixmap address, pitch/size, position, CLUT address, and sets `CUR_CTL_CLUT_UPDATE`. `sti_cursor_atomic_disable()` marks the STI plane disabling.

Control flow: The atomic check owns pixmap allocation because cursor size drives buffer size. Atomic update is purely register programming and status transition to `STI_PLANE_UPDATED`; the CRTC flush later enables it in the mixer. Cursor disable is finalized immediately by CRTC flush because cursor does not require GDP/HQVDP DMA retirement.

State/persistence: Cursor keeps current width/height, CLUT virtual/physical address, and DMA pixmap metadata. Plane status and FPS counters live in embedded `struct sti_plane`.

Dependencies/integration: Uses DRM plane helpers, DMA GEM framebuffer helpers, write-combined DMA allocation, VTG coordinate helpers, mixer/CRTC path through common plane status, and debugfs for register inspection.

Risks/test signals: No explicit destroy-time freeing is installed for pixmap/CLUT beyond partial create failure; devm lifetime and plane cleanup must match device teardown. Conversion assumes GEM CPU virtual address is valid. Test cursor size limits, repeated resize, negative/offscreen coordinates clamped by DRM state, debugfs CLUT/pixmap addresses, and cursor enable/disable over atomic commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_cursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_cursor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_cursor.h

Purpose: Provides the constructor declaration for the STI DRM cursor plane.

Important API: `sti_cursor_create(struct drm_device *drm_dev, struct device *dev, int desc, void __iomem *baseaddr, unsigned int possible_crtcs)` allocates/registers a cursor plane at a compositor register offset with a CRTC mask.

Control/state: The implementation owns all cursor-private state; the header only exposes a `struct drm_plane *` factory so the compositor can attach the cursor to a CRTC without knowing the CLUT/pixmap internals.

Dependencies/integration: Forward declares DRM and device types, keeping the compositor include light. The `desc` value is expected to be `STI_CURSOR` from `sti_plane.h`, though the header itself does not include that enum.

Risks/test signals: Constructor callers must provide a valid register base and possible-CRTC mask. Compile-time integration and KMS plane enumeration verify the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_cursor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_drv.c

Purpose: Top-level STI DRM module and component master. It registers all STI display platform drivers, creates the DRM device, binds subcomponents, initializes mode config/GEM/fbdev helpers, and exposes debugfs FPS controls.

Important APIs/functions: `sti_drm_init()` registers the platform driver array unless firmware-only mode is active. `sti_platform_probe()` sets a 32-bit DMA mask, populates OF children, and calls `drm_of_component_probe()`. `sti_bind()` allocates `drm_device`, runs `sti_init()`, binds all components, registers DRM, resets mode config, and starts generic client setup. `sti_cleanup()` shuts down KMS, unbinds components, and frees `sti_private`. `sti_drm_fps_get/set()` and `sti_drm_fps_dbg_show()` control/report per-plane FPS logging.

Control flow: Platform probe creates the component graph; master bind is the point where subdrivers create encoders, connectors, planes, CRTCs, and bridges. Errors unwind through DRM cleanup and `drm_dev_put()`.

State/persistence: `struct sti_private` is allocated with `kzalloc_obj`, stored in `drm_dev->dev_private`, and holds the compositor pointer after compositor bind. Plane FPS strings/counters are persistent per plane and toggled through debugfs.

Dependencies/integration: Uses DRM atomic helpers, GEM DMA helpers, fbdev DMA setup, OF component matching, and all local STI platform driver declarations.

Risks/test signals: `sti_platform_shutdown()` assumes `platform_get_drvdata()` returns a DRM device, but master setup stores the device via `dev_set_drvdata()` during `sti_init()`. Test probe/unbind failure paths, module unload, fbdev client creation, debugfs FPS toggling, and component bind ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_drv.h

Purpose: Declares shared top-level STI DRM private state and platform-driver exports.

Important types/APIs: `struct sti_private` stores the compositor pointer, an unused/legacy plane z-order property pointer, and the DRM device pointer. The header exports `sti_tvout_driver`, `sti_hqvdp_driver`, `sti_hdmi_driver`, `sti_hda_driver`, `sti_dvo_driver`, `sti_vtg_driver`, and `sti_compositor_driver` for the module driver array.

Control/state: The private object is allocated by `sti_init()` and receives the compositor pointer during compositor bind. Driver declarations let `sti_drv.c` register all display subdrivers as one module unit.

Dependencies/integration: Includes Linux platform device definitions and forward declares DRM/property/compositor types. It is included by most subdrivers that need `sti_private` or platform-driver declarations.

Risks/test signals: Adding/removing a subdriver requires keeping this export list and the registration array in sync. Build coverage and platform-driver probe logs are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_dvo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_dvo.c

Purpose: Implements the DVO/LVDS bridge and connector side of the STI display pipeline. It attaches to the LVDS encoder created by TVOUT, configures DVO clocks, AWG sync generation, LUT byte routing, and optional panel modes.

Important APIs/functions: `sti_dvo_probe()` allocates a DRM bridge, maps `dvo-reg`, gets `dvo_pix`, `dvo`, and optional parent clocks, parses `sti,panel`, and registers component ops. `sti_dvo_bind()` finds the LVDS encoder, adds/attaches the bridge, creates an LVDS connector, and attaches it to the encoder. `sti_dvo_set_mode()` copies the mode, selects main/aux parent clocks from the encoder CRTC mixer, sets clock rates, and selects `rgb_24bit_de_cfg`. `sti_dvo_pre_enable()` generates AWG code, enables clocks/panel, writes LUT routing, and enables the formatter; disable reverses this.

Control flow: The bridge mode-set chooses clock parents/rates before pre-enable writes hardware. Connector detect lazily resolves the DRM panel and reports connected only when found. Mode validation checks rounded pixel-clock tolerance.

State/persistence: `struct sti_dvo` persists current mode, clocks, panel reference, selected config, bridge, encoder pointer, and enabled flag. Debugfs exposes DVO registers and AWG microcode.

Dependencies/integration: Uses DRM bridge/connector/panel helpers, STI AWG utilities, TVOUT-created LVDS encoder, mixer identity for main/aux clock parent selection, and OF panel lookup.

Risks/test signals: `panel_node` is put immediately after parsing yet reused later, which is lifetime-sensitive. Clock enable errors are logged but do not abort pre-enable. Test panel detect, mode validation tolerance, bridge enable/disable, AWG generation failure, main/aux path clock-parent selection, and debugfs microcode dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_dvo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_gdp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_gdp.c

Purpose: Implements GDP graphics display planes for framebuffer scanout and overlays. GDP planes use DMA command nodes chained through `GAM_GDP_NVN` and synchronized with VTG field events.

Important APIs/functions: `sti_gdp_create()` allocates/registers a DRM universal plane, initializes DMA node banks, clocks, and VTG notifier. `sti_gdp_atomic_check()` validates format, DMA GEM backing, destination/source bounds, and sets GDP pixel-clock parent/rate when available. `sti_gdp_atomic_update()` builds top/bottom field nodes, calculates PML/PMP/size/VTG positions, handles progressive/interlaced NVN update rules, and posts the next node. `sti_gdp_field_cb()` tracks current top/bottom field and finalizes flushing disables. `sti_gdp_disable()` marks nodes ignored, unregisters VTG, disables clock, and marks the plane disabled.

Control flow: Two node banks avoid overwriting the node currently consumed by hardware. Atomic update chooses a free bank, fills top/bottom nodes, and either directly writes NVN or patches the current node chain depending on current hardware state and interlace field. CRTC flush enables the plane at the mixer after update.

State/persistence: `struct sti_gdp` persists register base, optional GDP pixel clock and parent clocks, two DMA node banks, current-field flag, VTG pointer, and embedded `sti_plane` status/FPS.

Dependencies/integration: Uses DRM atomic plane helpers, DMA GEM helpers, VTG coordinate helpers, compositor VTG lookup, mixer z-order/status programming, and debugfs node/register dumps.

Risks/test signals: Scaling is not supported; larger destinations are clamped and smaller are cropped with debug warnings. DMA node allocation has alignment checks but no cleanup path on partial failure. Test all supported formats, interlaced vs progressive updates, repeated atomic no-op detection, disable synchronization, GDP debugfs node addresses, and underflow status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_gdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_gdp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_gdp.h

Purpose: Exposes the GDP plane constructor to the compositor.

Important API: `sti_gdp_create()` takes the DRM device, parent device, STI plane descriptor, register base, possible-CRTC mask, and DRM plane type, returning the registered `struct drm_plane *`.

Control/state: The implementation hides command-node banks, clocks, and VTG callbacks behind the returned DRM plane. The `type` argument lets the compositor create the first GDP planes as primaries and later GDPs as overlays.

Dependencies/integration: Includes DRM plane definitions and forward declares device/DRM types. Callers must pass a descriptor from `enum sti_plane_desc` and a valid compositor register offset.

Risks/test signals: Wrong possible-CRTC masks or plane type assignment changes user-visible KMS topology. KMS plane listing and atomic commit tests cover the constructor contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_gdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hda.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hda.c

Purpose: Implements HD analog/component output as a DRM bridge and connector attached to the DAC encoder created by TVOUT. It programs supported video modes, AWG microcode, sampler/scaler coefficients, DAC clocks, and optional video DAC control registers.

Important APIs/functions: `sti_hda_probe()` allocates the bridge, maps `hda-reg` and optional `video-dacs-ctrl`, gets `pix` and `hddac` clocks, and adds the bridge/component. `sti_hda_bind()` finds the DAC encoder, attaches the bridge, creates a Component connector, and disables DACs at startup. `sti_hda_set_mode()` validates a mode against `hda_supported_modes`, sets `hddac` rate to 2x or 4x pixel clock based on category, and sets formatter pixel clock. `sti_hda_pre_enable()` enables clocks, selects filters/coefficients, enables DACs, writes scaler/sampler/AWG registers, and enables AWG. `sti_hda_disable()` disables AWG/DACs and clocks.

Control flow: Modes are fixed in a static table; connector mode enumeration duplicates those modes and marks the first preferred. Mode validation checks both table membership and rounded clock tolerance.

State/persistence: `struct sti_hda` stores current mode, register bases, clocks, bridge, DRM device, and enabled flag. Static AWG instruction arrays and coefficient tables encode supported timing categories.

Dependencies/integration: Uses DRM bridge/connector helpers, component framework, clocks, IO resources, TVOUT DAC encoder, and debugfs. TVOUT programs shared VIP routing while this file programs the analog formatter itself.

Risks/test signals: Several pre-enable error paths return after clocks are enabled without unwinding. Supported modes are narrow and interlaced support is explicitly absent in the chain. Test each advertised mode, clock tolerance, DAC power transitions, bridge enable/disable, debugfs AWG/register output, and probe without `video-dacs-ctrl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi.c

Purpose: Implements HDMI output as a DRM bridge/connector with HPD, EDID/DDC, infoframes, audio codec integration, CEC notifier updates, clock programming, PHY control, interrupts, and debugfs.

Important APIs/functions: `sti_hdmi_probe()` allocates the bridge, obtains DDC adapter, maps `hdmi-reg`, selects PHY ops from OF match data, gets `pix`, `tmds`, `phy`, and `audio` clocks, initializes HPD/waitqueue/IRQ/reset, and registers component ops. `sti_hdmi_bind()` finds the TMDS encoder, attaches the bridge, creates an HDMI-A connector with DDC, adds a colorspace property, registers `hdmi-codec`, initializes audio infoframe state, registers CEC notifier, and enables default interrupts. Bridge `mode_set`, `pre_enable`, and `disable` program rates, PHY, active area, interrupts, config bits, infoframes, audio, software reset, and teardown.

Control flow: IRQ top half reads/clears status and wakes the thread. Threaded IRQ updates HPD, emits DRM HPD events, wakes waiters for SW reset/PLL lock, and logs audio underruns. EDID modes are read through DRM EDID helpers and update CEC physical address. Audio callbacks configure N, channel-valid bits, infoframe, mute flat masks, and ELD access.

State/persistence: `struct sti_hdmi` stores current mode, register base, clocks, IRQ status, PHY ops, HPD/enabled flags, wait event, DDC adapter, colorspace, audio params, connector pointer, notifier, and bridge.

Dependencies/integration: Uses DRM bridge/connector/EDID/property helpers, Linux HDMI infoframe helpers, CEC notifier, sound `hdmi-codec`, local TX3G4C28 PHY ops, and VTG coordinate helpers.

Risks/test signals: Pre-enable sets `enabled = true` before PHY start failure and does not unwind clocks on failure. Infoframe register loops step by four but compare against word-count-like constants, so boundary review is important. Test HPD IRQ, EDID failure, color-space property updates, DVI vs HDMI config, audio channel counts/rates, CEC physical address invalidation, bridge disable cleanup, and debugfs infoframe dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi.h

Purpose: Defines shared HDMI types and register helpers used by the HDMI controller and PHY implementation.

Important APIs/types: `struct hdmi_phy_ops` provides `start` and `stop` hooks for PHY-specific code. `struct hdmi_audio_params` stores enabled state, sample width/rate, and CEA audio infoframe. `struct sti_hdmi` is the central HDMI runtime object: device, DRM device, mode, registers, clocks, IRQ/status, PHY ops, HPD wait state, reset, DDC adapter, colorspace, audio codec platform device, connector, CEC notifier, and bridge. `hdmi_read()`/`hdmi_write()` are exported for PHY code.

Control/state: Defines HPD/DLL lock register bits and default colorspace. The HDMI controller owns persistent bridge/connector/audio/CEC state while the PHY module manipulates serializer/PLL registers through the same mapped register space.

Dependencies/integration: Includes Linux HDMI, platform device, CEC notifier, and DRM bridge/mode/property headers.

Risks/test signals: Changes to `struct sti_hdmi` affect both controller and PHY compilation. PHY ops must be valid for the OF-compatible device. Build and HDMI bridge enable tests verify the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi_tx3g4c28phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi_tx3g4c28phy.c

Purpose: Provides PHY-specific start/stop operations for the TX3G4C28 HDMI serializer/PLL used by STiH407 HDMI.

Important APIs/functions: `sti_hdmi_tx3g4c28phy_start()` selects PLL input/output divider values for the requested pixel clock, programs PLL control, waits for DLL lock through the HDMI wait event, then programs serializer configuration, current control, and calibration registers. `sti_hdmi_tx3g4c28phy_stop()` keeps detection bits, clears PLL config, waits for lock deassertion, and logs if the PLL remains locked. `tx3g4c28phy_ops` exposes these hooks to `sti_hdmi.c`.

Control flow: Start rejects unsupported input clocks and TMDS clocks above 340 MHz. Divider selection is table-driven; source termination is enabled above 165 MHz. A board/SoC PHY config table optionally overrides external bits while internal control bits are masked out.

State/persistence: Uses `hdmi->mode.clock` and `hdmi->event_received` wait synchronization. It does not own separate allocated state.

Dependencies/integration: Depends on `hdmi_read()`/`hdmi_write()`, `struct sti_hdmi`, HDMI status bits, and interrupts from the HDMI controller to wake waiters for PLL lock transitions.

Risks/test signals: If HDMI interrupts are disabled or lost, start/stop wait until timeout and status polling decides success. Config table covers only up to 300 MHz despite a 340 MHz TMDS upper guard; higher clocks fall back to default serializer settings. Test clock ranges, PLL lock timeout, 165 MHz termination boundary, and bridge disable lock deassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi_tx3g4c28phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi_tx3g4c28phy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi_tx3g4c28phy.h

Purpose: Declares the TX3G4C28 HDMI PHY ops exported to the HDMI controller.

Important API: `extern struct hdmi_phy_ops tx3g4c28phy_ops` supplies the PHY `start` and `stop` callbacks selected by the HDMI OF match table.

Control/state: No state is declared here; the implementation operates on `struct sti_hdmi` provided by the controller.

Dependencies/integration: Includes `sti_hdmi.h` for `struct hdmi_phy_ops` and `struct sti_hdmi`. Used by `sti_hdmi.c` to populate `.data` for `st,stih407-hdmi`.

Risks/test signals: Header and implementation must agree on symbol name and ops lifetime. Build/link coverage catches mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi_tx3g4c28phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hqvdp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hqvdp.c

Purpose: Implements the HQVDP video processing plane. It exposes an NV12 overlay plane backed by an XP70 firmware processor, command-mailbox DMA buffers, scaling coefficient LUTs, deinterlacing setup, and VTG-driven bottom-field handling.

Important APIs/functions: `sti_hqvdp_probe()` maps registers, gets `hqvdp` and `pix_main` clocks, deasserts reset, resolves VTG, and registers component ops. `sti_hqvdp_bind()` creates the DRM plane. `sti_hqvdp_start_xp70()` requests `hqvdp-stih407.bin`, validates its header sizes, resets hardware, loads plug/PMEM/DMEM firmware sections, enables fetch, and waits for firmware ready. `sti_hqvdp_atomic_check()` validates DMA backing, sizes, scaling capability, starts firmware if needed, and registers VTG. `sti_hqvdp_atomic_update()` fills a free command with source addresses, pitches, viewport, output size, CSDI/deinterlace settings, HVSRC coefficients, and posts it to `HQVDP_MBX_NEXT_CMD`.

Control flow: Two command buffers are shared with firmware; free/current/next helpers avoid overwriting active commands. Interlaced input posts a top-field command and marks bottom-field pending; the VTG callback clones the current command, adjusts luma/chroma by half-pitch, posts a bottom-field command, and updates field FPS. Disable is synchronized by VTG flush and waits for firmware idle before dropping the pixel clock.

State/persistence: `struct sti_hqvdp` stores command DMA memory, physical base, XP70 initialized flag, VTG registration flag, pending bottom-field flag, clocks, reset, and embedded STI plane state.

Dependencies/integration: Uses DRM atomic plane helpers, firmware loader, DMA GEM helpers, compositor/mixer/VTG integration, `sti_hqvdp_lut.h` coefficient tables, and debugfs command/mailbox dumps.

Risks/test signals: Firmware absence leaves the plane unable to start but `atomic_check()` continues after calling start unless later state exposes failure. Preallocated command buffers are never explicitly freed in remove. Scaling math divides by destination dimensions, so zero-sized states depend on earlier DRM validation. Test firmware load errors, NV12-only format, scaling limits, interlaced bottom-field posting, VTG unregister, mailbox debugfs, and disable idle timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hqvdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hqvdp_lut.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hqvdp_lut.h

Purpose: Supplies static legacy HVSRC scaling coefficient lookup tables for HQVDP luma/chroma horizontal and vertical scaling.

Important APIs/types: Defines `NB_COEF` as 128, shift constants for LUT classes A through F, and arrays such as `coef_lut_a_legacy`, `coef_lut_b`, `coef_lut_c_y_legacy`, `coef_lut_c_c_legacy`, through F variants. These arrays are copied into `struct sti_hqvdp_hvsrc` command fields by `sti_hqvdp_update_hvsrc()`.

Control/state: The header is data-only. HQVDP chooses tables by scale factor thresholds: stronger downscale picks later legacy LUT classes, unity uses LUT B, and upscale falls back to LUT A. Shift values are packed into horizontal/vertical shift registers alongside copied coefficients.

Dependencies/integration: Included only by `sti_hqvdp.c`. It assumes `u32` is available from prior includes in that compilation unit.

Risks/test signals: Since tables are compile-time constants, errors show as visual artifacts rather than runtime failures. Table size must match `NB_COEF` and command array fields. Test by exercising scale ratios around each threshold and comparing HQVDP debugfs LUT names and visual output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hqvdp_lut.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_mixer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_mixer.c

Purpose: Implements low-level mixer register programming for main/aux composition: background color/area, active video area, plane enable masks, z-order depth, and debugfs state.

Important APIs/functions: `sti_mixer_create()` allocates `struct sti_mixer` and records id/register base. `sti_mixer_active_video_area()` writes active video and background bounds from DRM mode via VTG coordinate helpers, sets the module-param background color, and enables background. `sti_mixer_set_plane_depth()` maps STI plane descriptors to crossbar depth ids and updates `GAM_MIXER_CRB` using normalized zpos. `sti_mixer_set_plane_status()` maps plane descriptors to `GAM_MIXER_CTL` masks and enables/disables layers. `sti_mixer_debugfs_init()` exposes register dumps for main/aux mixers.

Control flow: CRTC mode set programs active/background geometry; CRTC atomic flush calls depth then status for updated planes and status false for disabling planes. Cursor depth is immutable/no-op.

State/persistence: Mixer has only dev, register base, id, embedded CRTC, and status. Background color is a writable module parameter `bkgcolor`.

Dependencies/integration: Uses DRM debugfs, local plane descriptors/status, VTG coordinate conversion, and CRTC ownership through `to_sti_mixer`.

Risks/test signals: Depth update searches existing plane assignment but can operate with an uninitialized `mask` if the plane id is not found before the loop completes; this path deserves review. Test zpos changes, layer enable/disable, background color parameter, active area for multiple modes, and mixer debugfs CRB/CTL decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_mixer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_mixer.h

Purpose: Defines the STI mixer object and its programming interface for CRTC and plane flush code.

Important APIs/types: `struct sti_mixer` embeds `struct drm_crtc`, register base, device pointer, mixer id, and status. `to_sti_mixer()` converts a CRTC pointer to the containing mixer. Public functions create mixers, set plane status/depth, configure active video area, set background status, and initialize debugfs. `STI_MIXER_MAIN` and `STI_MIXER_AUX` identify the two compositor paths.

Control/state: `enum sti_mixer_status` tracks CRTC lifecycle readiness and deferred disabling. `GAM_MIXER_NB_DEPTH_LEVEL` fixes z-order slots to six programmable levels.

Dependencies/integration: Includes DRM CRTC/debugfs/file headers and `sti_plane.h`. Used by compositor construction, CRTC lifecycle, TVOUT path selection, GDP/HQVDP debug messages, and output bridge clock-parent decisions.

Risks/test signals: The embedded CRTC layout is a core ABI inside this driver. Any change to ids/status must be validated through modeset and output path selection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_mixer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_plane.c

Purpose: Provides common STI plane helpers shared by GDP, HQVDP, cursor, and mixer/CRTC code.

Important APIs/functions: `sti_plane_to_str()` maps plane descriptors to readable names. `sti_plane_update_fps()` tracks frame and field counters over a 3-second interval, formats FPS/FIPS strings from the active framebuffer, and optionally logs them. `sti_plane_init_property()` attaches zpos properties and emits debug mapping. Internal helpers choose default zpos: primary 0, overlay 1, cursor 7, with mutable zpos for primary/overlay and immutable cursor zpos.

Control flow: Plane implementations call `sti_plane_update_fps()` after hardware updates or field events. The top-level driver debugfs toggles `fps_info.output`; the CRTC flush uses `plane->status` but this file only defines common property and accounting helpers.

State/persistence: FPS counters, timestamps, output flag, and formatted strings live in `struct sti_fps_info` embedded in each `struct sti_plane`.

Dependencies/integration: Uses DRM blend/zpos properties, framebuffer format metadata, GEM DMA includes, and local plane enums. Debugfs FPS reporting in `sti_drv.c` reads the strings maintained here.

Risks/test signals: FPS formatting casts fourcc to a char string and depends on framebuffer state remaining valid. Test zpos property ranges, cursor immutable zpos, FPS enable bitmask, field-rate reporting for interlaced HQVDP, and no-FB transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_plane.h

Purpose: Defines common STI plane descriptors, status states, FPS accounting, and helper prototypes.

Important types/APIs: `enum sti_plane_type`, `enum sti_plane_id_of_type`, and `enum sti_plane_desc` encode GDP0-3, HQVDP0, cursor, and background. `enum sti_plane_status` drives cross-module atomic flow (`READY`, `UPDATED`, `DISABLING`, `FLUSHING`, `DISABLED`). `struct sti_plane` embeds a DRM plane plus descriptor, status, and FPS info. `to_sti_plane()` converts DRM plane to STI plane. Helpers expose string conversion, FPS update, and property init.

Control/state: Status values are the handshake between plane atomic helpers and CRTC flush/VTG callbacks. `STI_PLANE_TYPE_MASK` lets code group GDP/VDP/cursor/background classes.

Dependencies/integration: Includes DRM atomic helper definitions and is included by nearly every STI plane/mixer/CRTC component.

Risks/test signals: Plane descriptor bit layout is relied on by comparisons such as overlay disable checks. Any enum change needs CRTC/mixer/GDP/HQVDP validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_tvout.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_tvout.c

Purpose: Implements the shared TVOUT glue block and creates the HDMI, HDA, and DVO encoders used by the output bridge drivers. It routes main/aux mixer output to VIP blocks, configures CSC matrices, sync sources, clipping/rounding/channel order, HD DAC power, and debugfs.

Important APIs/functions: `sti_tvout_probe()` maps `tvout-reg`, deasserts reset, and registers component ops. `sti_tvout_bind()` creates HDMI TMDS, HDA DAC, and DVO LVDS encoders with common encoder funcs and type-specific helper funcs. `tvout_preformatter_set_matrix()` writes BT.709 or BT.601 RGB-to-YCbCr matrices by mode height. `tvout_hdmi_start()`, `tvout_hda_start()`, and `tvout_dvo_start()` select sync source and VIP input for main/aux path, set color order, clipping, rounding, input format, and output-specific selection. Encoder enable helpers call those start functions; disable helpers clear VIP state and DAC power.

Control flow: TVOUT creates encoders first; separate bridge/component drivers later find encoders by type and attach connectors/bridges. Encoder helper enable is path-sensitive via `sti_crtc_is_main()`.

State/persistence: `struct sti_tvout` stores DRM device, register base, reset, encoder pointers, and debugfs registration flag. `struct sti_tvout_encoder` embeds each DRM encoder and back-pointer.

Dependencies/integration: Uses component framework, DRM encoder helpers, reset API, CRTC path selection, VTG sync ids, and output-specific bridge drivers. It is the glue between compositor mixer paths and physical outputs.

Risks/test signals: `sti_tvout_create_encoders()` assumes all three encoder allocations succeed before setting clone masks. HDA helper uses `.commit` while HDMI/DVO use `.enable`, reflecting older helper semantics. Test encoder creation failure handling, clone masks, main/aux routing for each output, VIP debugfs, CSC matrix choice at 720-line boundary, and DAC power-off on disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_tvout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vid.c

Purpose: Implements the VID mixer-side video layer programmed when the HQVDP plane is committed. It controls viewport registers, masking, color conversion matrices, PSI defaults, and debugfs.

Important APIs/functions: `sti_vid_create()` allocates `struct sti_vid`, records id/register base, and calls `sti_vid_init()`. `sti_vid_commit()` unmasks the VID layer, aligns destination dimensions to even values, converts destination coordinates through VTG helpers, writes viewport origin/stop, and selects BT.709 or BT.601 YCbCr-to-RGB coefficients based on source height. `sti_vid_disable()` masks the layer. `vid_debugfs_init()` exposes register state.

Control flow: The compositor creates VID before planes. During CRTC atomic flush, when an updated plane has descriptor `STI_HQVDP_0`, CRTC calls `sti_vid_commit(compo->vid[0], p->state)` after enabling plane depth/status. Disabling HQVDP causes `sti_vid_disable()`.

State/persistence: `struct sti_vid` stores device, register base, and id. Hardware registers persist viewport, coefficients, alpha, PSI, and ignore-mask state.

Dependencies/integration: Uses DRM plane state, VTG coordinate conversion, HQVDP plane descriptor via CRTC, and mixer enable masks.

Risks/test signals: Colorimetry selection by source height is a coarse heuristic. VID assumes one HQVDP/VID pair at `vid[0]`. Test HQVDP commits at SD/HD heights, viewport alignment, disable mask, debugfs coefficient dump, and mixer interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vid.h

Purpose: Declares the VID layer object and public operations used by compositor and CRTC code.

Important APIs/types: `struct sti_vid` stores device, register base, and id. `sti_vid_create()` constructs and initializes a VID block. `sti_vid_commit()` programs VID viewport/color conversion from a DRM plane state. `sti_vid_disable()` masks the VID layer. `vid_debugfs_init()` registers debugfs dumps.

Control/state: The VID block is not a DRM plane itself; it is a hardware companion to the HQVDP DRM plane and is driven from CRTC flush based on plane descriptor.

Dependencies/integration: Forward declarations are implicit from included build context; implementation depends on DRM plane state and DRM minor. Used by compositor setup and CRTC atomic flush.

Risks/test signals: Header lacks explicit forward declarations for some referenced structs, relying on include order in users. Build coverage and HQVDP display tests validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_vid.h -->

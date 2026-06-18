# subset-b-003576 Research

Grouped research for GMA500 SDVO/IRQ registers, the Generic USB Display DRM driver, and Hisilicon HIBMC DisplayPort AUX support under `sources/distributed-fs/ceph-client/drivers/gpu/drm`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_reg.h

## Purpose
`psb_intel_reg.h` is the main display register map for the GMA500/Poulsbo Intel-derived display block. It names MMIO offsets and bitfields for GPIO/GMBUS, backlight PWM, panel power sequencing, CRTC timing, DPLL programming, analog/SDVO/LVDS/MIPI/DP ports, pipe status/vblank accounting, planes, cursors, palettes, hotplug, sideband DPIO, and Cedarview DisplayPort AUX/M/N timing.

## Important APIs, Types, And Functions
The file exports preprocessor constants rather than C functions. Important register families include `GPIOA` through `GPIOH`, `GMBUS0` through `GMBUS5`, `BLC_PWM_CTL*`, `PP_STATUS`, `PP_CONTROL`, `PFIT_CONTROL`, `DPLL_A/B`, `DPLL_A_MD`, `DPLL_B_MD`, `ADPA`, `PORT_HOTPLUG_EN`, `PORT_HOTPLUG_STAT`, `SDVOB`, `SDVOC`, `LVDS`, `PIPEACONF`/`PIPEBCONF`/`PIPECCONF`, `PIPEASTAT`/`PIPEBSTAT`/`PIPECSTAT`, framebuffer counter registers, plane registers such as `DSPACNTR` and `DSPASURF`, cursor registers, interrupt registers `IER/IIR/IMR/ISR`, MIPI DSI registers, and DP registers such as `DP_B`, `DP_C`, `DPB_AUX_CH_CTL`, and `PIPE_GMCH_DATA_M(pipe)`.

It also defines utility macros such as `PSB_MASK`, `SET_FIELD`, `GET_FIELD`, and `_PIPE(pipe, a, b)` for bitfield and per-pipe address construction.

## Control Flow
There is no runtime control flow in this header. Driver code includes it, reads/writes the named MMIO registers through GMA500 accessors, and uses the bit masks to compose values for display bring-up, mode setting, hotplug handling, vblank interrupts, panel power sequencing, and link training.

## State And Persistence
All state represented here is hardware state. Writes can alter I2C pin direction, GMBUS transaction state, backlight PWM duty cycle, panel power timing, DPLL clocking, port enablement, pipe timing, plane base/stride/surface state, interrupt enables/status bits, MIPI DSI FIFOs, and DisplayPort link state. Those values persist in the device until reset or overwritten.

## Dependencies And Integration Points
The header is used by GMA500 display, IRQ, SDVO, LVDS, MIPI, DP, GMBUS, and power-management code. `psb_irq.c` uses the pipe status, pipe frame, hotplug, and interrupt constants. `psb_intel_sdvo.c` uses `SDVOB`, `SDVOC`, `SDVO_*`, `GMBUS_*`, and hotplug bits. The DP/MIPI constants integrate with other GMA500 display paths not in this work item.

## Risks
This file is chip-generation sensitive. Several definitions share names across Poulsbo, Moorestown, Medfield, and Cedarview with different semantics or comments, so using the wrong constant on the wrong platform can program reserved bits. Interrupt status bits are generally write-one-to-clear or sticky, which requires careful masking. The macro `_PIPE` assumes regular pipe register spacing and only fits the paired registers for which it was written.

## Test Signals
Useful validation is successful mode setting across VGA, SDVO, LVDS, MIPI, and DP paths; stable GMBUS/DDC transactions; correct backlight and panel power sequencing; hotplug status bits clearing and re-firing correctly; vblank counters increasing only on enabled pipes; no FIFO underrun or HDMI audio underrun bits during modesets; and DP AUX/link training operating with the expected M/N and lane settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_sdvo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_sdvo.c

## Purpose
`psb_intel_sdvo.c` implements SDVO encoder and connector support for the GMA500 DRM driver. It discovers an SDVO device over the GMBUS/I2C control channel, creates DRM connectors for TMDS/DVI/HDMI, VGA, TV, and LVDS outputs advertised by the SDVO device, handles DDC proxying, validates and programs modes, controls DPMS, and exposes supported TV/LVDS enhancement properties.

## Important APIs, Types, And Functions
The central private types are `struct psb_intel_sdvo`, which embeds `struct gma_encoder` and stores the SDVO register, I2C adapter, DDC proxy, target address, capabilities, attached outputs, pixel clock limits, HDMI/audio flags, TV/LVDS mode state, pixel multiplier, input DTD, and saved register value; and `struct psb_intel_sdvo_connector`, which embeds `struct gma_connector` and stores per-connector output flags, forced audio state, TV format property, enhancement DRM properties, current/max enhancement values, and margin state.

The exported entry point is `psb_intel_sdvo_init(struct drm_device *dev, int sdvo_reg)`. Major internal helpers include `psb_intel_sdvo_read_byte()`, `psb_intel_sdvo_write_cmd()`, `psb_intel_sdvo_read_response()`, `psb_intel_sdvo_get_value()`, `psb_intel_sdvo_set_value()`, `psb_intel_sdvo_mode_fixup()`, `psb_intel_sdvo_mode_set()`, `psb_intel_sdvo_dpms()`, `psb_intel_sdvo_detect()`, `psb_intel_sdvo_get_modes()`, `psb_intel_sdvo_set_property()`, `psb_intel_sdvo_output_setup()`, connector-specific init routines, and the DDC proxy algorithm.

## Control Flow
Initialization allocates the SDVO encoder, chooses the target I2C address from VBT mappings or SDVOB/SDVOC defaults, selects the GMBUS adapter and speed, registers an I2C DDC proxy, initializes the DRM encoder, probes the first 0x40 SDVO I2C registers to confirm device presence, marks hotplug support, reads device capabilities, creates connectors according to the advertised output flags, selects the DDC bus, targets SDVO input 0, and reads the input pixel clock range.

Command flow writes SDVO arguments into descending `SDVO_I2C_ARG_*` registers, writes the opcode, then polls `SDVO_I2C_CMD_STATUS` up to five times with 15 microsecond delays before reading response bytes. Mode fixup prepares preferred input timing for TV/LVDS and applies the SDVO pixel multiplier. Mode set maps input 0 to the attached output, programs output and input DTDs, selects HDMI or DVI encode mode, sets TV format when needed, sets clock multiplier, composes `SDVOB` or `SDVOC`, selects pipe B when required, optionally enables SDVO audio, and writes both SDVO registers twice to match the BIOS workaround. DPMS disables active outputs and the SDVO port on off, or enables the port, waits two vblanks, checks trained inputs, and re-enables active outputs on on.

Detection asks `GET_ATTACHED_DISPLAYS`, delays for possible TV outputs, filters against the connector output flag, and for TMDS reads EDID through the SDVO DDC proxy and fallback analog DDC to decide HDMI/audio state. Mode enumeration uses EDID for digital/analog, fixed DDC or VBT modes for LVDS, and SDVO TV resolution commands for TV connectors. Property changes update local state, issue SDVO enhancement commands for relevant TV/LVDS properties, and force a CRTC modeset when the encoder is active.

## State And Persistence
Persistent software state lives in the SDVO encoder and connector objects: selected DDC bus, attached output mask, HDMI/audio flags, TV format index, LVDS fixed mode, pixel clock limits, saved SDVO register value, and enhancement property values. Hardware state lives in the SDVO device command register space and GMA500 SDVO MMIO registers. The driver also registers an I2C adapter for the DDC proxy and creates DRM connector/encoder objects that persist until connector or encoder destroy.

## Dependencies And Integration Points
This code depends on DRM KMS helper callbacks, GMA500 wrappers from `psb_drv.h` and `psb_intel_drv.h`, SDVO command definitions from `psb_intel_sdvo_regs.h`, register constants from `psb_intel_reg.h`, GMBUS adapters and VBT mappings in `struct drm_psb_private`, EDID helpers, GMA connector/encoder helpers, and optional hotplug support through `dev_priv->hotplug_supported_mask`.

## Risks
The command protocol is timing-sensitive and assumes register layouts from the SDVO spec. The DDC bus selection has an explicit hard-coded fallback to bus 2, so boards with unusual VBT mappings may fail EDID detection. Several HDMI paths are stubs or disabled, including AVI infoframe programming and HDMI properties, so HDMI sink/audio support is incomplete. The SDVO register write workaround writes both SDVOB and SDVOC twice and preserves only selected bits; mistakes can disturb the other SDVO port. Property changes can trigger full CRTC modesets. LVDS fixed-mode handling depends on EDID or VBT availability.

## Test Signals
Test signals include successful `psb_intel_sdvo_init()` on both SDVOB and SDVOC addresses, correct connector creation for advertised output flags, reliable EDID reads through the DDC proxy and fallback path, mode validation respecting SDVO clock limits and LVDS fixed panel bounds, working DPMS off/on with trained input status, correct TV mode enumeration and enhancement property programming, hotplug events for SDVO status bits, and no regressions in vblank/mode setting after property changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_sdvo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_sdvo_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_sdvo_regs.h

## Purpose
`psb_intel_sdvo_regs.h` defines the SDVO command protocol, I2C register addresses, response statuses, packed request/reply structures, output flag bits, TV format maps, timing layouts, enhancement controls, LVDS panel data, power states, and HDMI command IDs used by the GMA500 SDVO driver.

## Important APIs, Types, And Functions
The header exports output flags such as `SDVO_OUTPUT_TMDS0`, `SDVO_OUTPUT_RGB0`, `SDVO_OUTPUT_CVBS0`, `SDVO_OUTPUT_SVID0`, `SDVO_OUTPUT_LVDS0`, and the corresponding second-channel flags. Important packed types include `struct psb_intel_sdvo_caps`, `struct psb_intel_sdvo_dtd`, `struct psb_intel_sdvo_pixel_clock_range`, `struct psb_intel_sdvo_preferred_input_timing_args`, `struct psb_intel_sdvo_get_trained_inputs_response`, `struct psb_intel_sdvo_in_out_map`, `struct psb_intel_sdvo_tv_format`, SDTV/HDTV resolution request/reply structures, `struct psb_sdvo_panel_power_sequencing`, `struct psb_intel_sdvo_enhancements_reply`, `struct psb_intel_sdvo_enhancement_limits_reply`, and `struct psb_intel_sdvo_encode`.

Command constants cover device caps, firmware, trained inputs, active outputs, input/output maps, hotplug, target input/output, timing get/set, preferred input timing generation, pixel clock ranges, clock multipliers, TV format/resolution, encoder and display power, panel power sequencing, backlight/ambient light, enhancement get/set commands, DDC bus switching, and HDMI encode/colorimetry/audio/hardware buffer operations.

## Control Flow
The header has no executable flow. `psb_intel_sdvo.c` uses the I2C register constants to marshal arguments, writes one of the `SDVO_CMD_*` opcodes, reads `SDVO_I2C_CMD_STATUS`, and interprets the response bytes by casting them into the packed structures defined here.

## State And Persistence
The constants describe state stored inside the SDVO device firmware and encoder hardware: active output masks, selected target input/output, DTD timing data, clock multiplier, TV format, power state, panel sequencing, backlight, ambient light, enhancement levels, DDC bus switch, HDMI encode mode, colorimetry, audio state, and infoframe buffer state. The header itself stores no state.

## Dependencies And Integration Points
It depends on kernel integer typedefs and packed bitfield behavior. It is paired directly with `psb_intel_sdvo.c` and indirectly with the DRM connector property layer, EDID/DDC code, and GMA500 SDVO MMIO definitions in `psb_intel_reg.h`.

## Risks
The packed bitfield structures depend on compiler layout matching the SDVO firmware protocol. Some comments contain historical typos, and the HDMI command set is more complete than the implementation, which can make apparent support misleading. Command status handling in users must account for `PENDING`, `TARGET_NOT_SPECIFIED`, and unsupported responses. TV and HDTV resolution structures are dense bitmaps where index ordering must match the driver's mode table.

## Test Signals
Validation should confirm `BUILD_BUG_ON` structure sizes in the implementation remain true, device capabilities parse correctly, timing DTD round-trips match DRM mode fields, TV format bitmaps produce the intended property names and modes, enhancement max/current reads map to the right properties, and unsupported command statuses are handled without leaving the SDVO device in a partially programmed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_sdvo_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_irq.c

## Purpose
`psb_irq.c` implements interrupt installation, masking, dispatch, vblank enable/disable, page-flip event completion, SGX fault logging, hotplug dispatch, and vblank counter reads for the GMA500 DRM driver.

## Important APIs, Types, And Functions
Exported functions are `gma_irq_preinstall()`, `gma_irq_postinstall()`, `gma_irq_install()`, `gma_irq_uninstall()`, `gma_crtc_enable_vblank()`, `gma_crtc_disable_vblank()`, `gma_crtc_get_vblank_counter()`, `gma_enable_pipestat()`, and `gma_disable_pipestat()`. Internal helpers are `gma_pipestat()`, `gma_pipeconf()`, `gma_pipe_event_handler()`, `gma_vdc_interrupt()`, `gma_sgx_interrupt()`, and the IRQ top half `gma_irq_handler()`.

## Control Flow
`gma_irq_install()` optionally enables MSI, rejects disconnected IRQs, masks and clears hardware in `gma_irq_preinstall()`, requests a shared PCI IRQ, and calls `gma_irq_postinstall()`. The postinstall step enables SGX 2D/MMU-fault interrupts, enables the VDC interrupt mask, configures per-pipe vblank pipestat bits for already enabled vblank users, and enables hotplug if the platform ops provide it.

The IRQ handler reads `PSB_INT_IDENTITY_R` under `irqmask_lock`, classifies display, SGX, and hotplug causes, applies the current `vdc_irq_mask`, then dispatches display events to `gma_vdc_interrupt()`, SGX events to `gma_sgx_interrupt()`, and hotplug to `dev_priv->ops->hotplug()`. Display pipe handling reads the relevant pipe status register, intersects enabled and status bits, repeatedly writes back the register to clear sticky bits, calls `drm_handle_vblank()`, and sends any pending page-flip vblank event under `dev->event_lock`.

Vblank enable checks that the pipe is enabled, updates `vdc_irq_mask`, writes interrupt mask/enable registers, and enables the pipe vblank status bit. Disable clears the corresponding pipe interrupt bit and disables pipestat. The vblank counter reads the high and low frame counter registers with a high-register stability loop.

## State And Persistence
Software state is held in `dev_priv->vdc_irq_mask`, `dev_priv->pipestat[]`, `dev_priv->irq_enabled`, `dev_priv->use_msi`, and each CRTC's pending `page_flip_event`. Hardware state includes VDC interrupt mask/enable/identity registers, pipe status registers, SGX host interrupt enable/clear/status registers, hotplug status, and per-pipe frame counters.

## Dependencies And Integration Points
The file depends on GMA500 register accessors from `psb_drv.h`, power gating helpers from `power.h`, display constants from `psb_intel_reg.h`, SGX constants from `psb_reg.h`, DRM vblank/event helpers, PCI IRQ/MSI APIs, and platform operations for hotplug and hotplug enable. It is declared by `psb_irq.h`.

## Risks
Pipe selection helpers call `BUG()` for invalid pipe indexes. Clearing pipe status uses a large retry loop for sticky bits and may still fail, producing errors. Interrupt mask updates are protected by `irqmask_lock`, but power-gated display access can fail and leave software masks out of sync with hardware. The hotplug identity bit is noted as overloaded on some devices. `gma_irq_uninstall()` preserves some non-display masks, so ordering with other engines matters.

## Test Signals
Useful tests include IRQ install/uninstall across MSI and shared-IRQ paths, vblank enable failure on disabled pipes, correct vblank event delivery and `drm_crtc_vblank_put()` balancing for page flips, stable frame counter increments, SGX fault logs and clears on induced faults, hotplug callback execution and `PORT_HOTPLUG_STAT` clearing, and no interrupt storms after repeated DPMS or suspend/resume cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_irq.h

## Purpose
`psb_irq.h` declares the GMA500 interrupt and vblank support functions implemented in `psb_irq.c`.

## Important APIs, Types, And Functions
It forward-declares `struct drm_crtc` and `struct drm_device` and exposes IRQ lifecycle functions `gma_irq_preinstall()`, `gma_irq_postinstall()`, `gma_irq_install()`, and `gma_irq_uninstall()`. It also exposes CRTC vblank hooks `gma_crtc_enable_vblank()`, `gma_crtc_disable_vblank()`, `gma_crtc_get_vblank_counter()`, plus pipe status mask helpers `gma_enable_pipestat()` and `gma_disable_pipestat()`.

## Control Flow
There is no executable flow in the header. The DRM driver and CRTC/vblank setup code include it to wire IRQ lifecycle callbacks and vblank operations into probe, teardown, and atomic/page-flip paths.

## State And Persistence
The header owns no state. The declared functions manipulate `struct drm_psb_private` interrupt masks, pipe status software shadows, PCI IRQ state, SGX interrupt registers, VDC interrupt registers, and DRM vblank/event state.

## Dependencies And Integration Points
The prototypes require `u32` and `struct drm_psb_private` to be visible or forward-declared by including code, even though this header only forward-declares DRM core types. It integrates `psb_irq.c` with the rest of the GMA500 DRM driver.

## Risks
Because `struct drm_psb_private` is not forward-declared here, include ordering matters for users of `gma_enable_pipestat()` and `gma_disable_pipestat()`. Prototype drift from `psb_irq.c` would break the driver's IRQ wiring at compile time.

## Test Signals
Compile coverage of all including translation units is the main signal. Runtime validation is inherited from `psb_irq.c`: successful IRQ install, working vblank hooks, and clean uninstall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_reg.h

## Purpose
`psb_reg.h` defines Poulsbo/SGX graphics-core and 2D blitter register offsets, event bits, BIF fault fields, 2D command block encodings, ROP constants, scene/scheduler constants, and power-management register masks used by the GMA500 driver.

## Important APIs, Types, And Functions
The header is macro-only. Important SGX/core registers include `PSB_CR_CLKGATECTL`, `PSB_CR_CORE_ID`, `PSB_CR_CORE_REVISION`, `PSB_CR_SOFT_RESET`, `PSB_CR_EVENT_HOST_ENABLE`, `PSB_CR_EVENT_STATUS`, `PSB_CR_EVENT_HOST_CLEAR`, their second-register variants, BIF registers such as `PSB_CR_BIF_CTRL`, `PSB_CR_BIF_INT_STAT`, `PSB_CR_BIF_FAULT`, and 2D status/control registers such as `PSB_CR_2D_SOCIF` and `PSB_CR_2D_BLIT_STATUS`.

The 2D command definitions include block headers like `PSB_2D_CLIP_BH`, `PSB_2D_CTRL_BH`, `PSB_2D_BLIT_BH`, source/destination/pattern/mask surface blocks, clip and stride/address masks, alpha and color-key controls, rotation/copy-order flags, and ROP constants such as `PSB_2D_ROP3_SRCCOPY`. Power constants include PUNIT/APM registers and masks for video, display, and graphics power gating.

## Control Flow
The header has no executable code. Consumers compose GPU command buffers or register writes using the constants, and interrupt handling reads/writes event status and clear registers using these bit definitions.

## State And Persistence
The definitions describe persistent GPU hardware state: clock gating, core reset, event enables/status, BIF page-fault status and fault address, USE/PDS code base addresses, 2D blitter command state, scene memory cookies, and power-gating status. The header stores no C state.

## Dependencies And Integration Points
`psb_irq.c` uses the SGX event and BIF fault constants to enable, decode, log, and clear SGX interrupts. Other GMA500 acceleration and power-management files use the 2D command and PUNIT definitions. It complements `psb_intel_reg.h`, which covers display-side registers.

## Risks
The register and command encodings are low-level and mostly untyped, so incorrect shifts or masks can corrupt command streams or acknowledge the wrong interrupt. Many addresses are specific to the Poulsbo/SGX block and should not be applied to unrelated GMA500 display generations. Fault interpretation in IRQ code depends on these bit meanings matching the hardware revision.

## Test Signals
Validation includes SGX interrupt enable/clear behavior, correct BIF fault reason and address logging, 2D blit command completion interrupts, successful accelerated copy/fill paths where present, no unexpected GPU resets after clock-gating/power changes, and clean suspend/resume of power-gated display and graphics blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/Kconfig

## Purpose
`gud/Kconfig` defines the kernel configuration option for the Generic USB Display DRM driver.

## Important APIs, Types, And Functions
It declares `config DRM_GUD` as a tristate option named "GUD USB Display". The option depends on `DRM`, `USB`, and `MMU`, and selects `LZ4_COMPRESS`, `DRM_CLIENT_SELECTION`, `DRM_KMS_HELPER`, `DRM_GEM_SHMEM_HELPER`, and `BACKLIGHT_CLASS_DEVICE`.

## Control Flow
There is no runtime flow. During kernel configuration, enabling this option controls whether `drivers/gpu/drm/gud/Makefile` builds the `gud` module or built-in object.

## State And Persistence
The file stores build-time configuration state only. If selected as a module, the resulting module is named `gud`.

## Dependencies And Integration Points
The selected helpers match the implementation's use of USB control/bulk transfers, DRM KMS helpers, GEM shmem framebuffers, LZ4 compression, DRM clients/fbdev setup, and backlight registration.

## Risks
Missing a selected dependency would surface as compile or link failures in `gud_drv.c`, `gud_pipe.c`, or `gud_connector.c`. The `MMU` dependency is important because the driver allocates vmalloc buffers and maps them into scatterlists for USB bulk transfer.

## Test Signals
Configuration tests should cover built-in and module builds with `CONFIG_DRM_GUD=y/m`, confirm required helper symbols are selected, and verify the `gud` module autoloads for the supported USB IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/Makefile

## Purpose
`gud/Makefile` defines the object composition for the Generic USB Display DRM driver.

## Important APIs, Types, And Functions
It builds `gud.o` from `gud_drv.o`, `gud_pipe.o`, and `gud_connector.o`, and adds it to the kernel build when `CONFIG_DRM_GUD` is enabled.

## Control Flow
There is no runtime control flow. Kbuild uses `gud-y` to link the driver core, framebuffer flushing pipeline, and connector support into one module or built-in object.

## State And Persistence
The file owns only build graph state.

## Dependencies And Integration Points
The object list corresponds to the internal API split in `gud_internal.h`: `gud_drv.c` provides probe and USB control helpers, `gud_pipe.c` provides plane/CRTC update and bulk flushing, and `gud_connector.c` provides connector enumeration, EDID/mode handling, properties, and backlight integration.

## Risks
Omitting one object would produce unresolved symbols or a driver that probes but cannot expose connectors or flush pixels. Adding new source files requires updating this list.

## Test Signals
Build tests with `CONFIG_DRM_GUD=m` should produce `gud.ko` containing all three implementation units and no unresolved internal symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_connector.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_connector.c

## Purpose
`gud_connector.c` implements dynamic connector discovery and connector-side behavior for the Generic USB Display driver. It translates USB protocol connector descriptors, statuses, EDID, display modes, TV/backlight properties, and connector state into DRM connector and encoder objects.

## Important APIs, Types, And Functions
`struct gud_connector` embeds a `drm_connector`, a simple `drm_encoder`, optional `backlight_device`, a backlight work item, a supported-property list, initial TV state, and initial brightness. Public internal functions are `gud_connector_fill_properties()` and `gud_get_connectors()`.

Key helpers include `gud_connector_detect()`, `gud_connector_get_modes()`, `gud_connector_atomic_check()`, `gud_connector_reset()`, `gud_connector_add_tv_mode()`, `gud_connector_property_lookup()`, `gud_connector_tv_state_val()`, `gud_connector_add_properties()`, `gud_connector_create()`, and the backlight work/update/register callbacks.

## Control Flow
`gud_get_connectors()` requests `GUD_REQ_GET_CONNECTORS`, validates that the response is a non-empty array of connector descriptors, and creates each connector in order. Creation maps GUD connector type values to DRM connector types, initializes connector helpers and funcs, verifies the DRM-assigned connector index matches the protocol index, applies polling/interlace/doublescan flags, requests supported connector properties, creates a simple encoder for the single GUD CRTC, and attaches it.

Detection optionally sends `GUD_REQ_SET_CONNECTOR_FORCE_DETECT`, reads `GUD_REQ_GET_CONNECTOR_STATUS`, maps connected/disconnected/unknown status to DRM, and increments the epoch counter when the device reports status change. Mode discovery first tries a protocol EDID blob via `GUD_REQ_GET_CONNECTOR_EDID`; if valid and not an override, it uses DRM EDID modes, otherwise it requests protocol display modes with `GUD_REQ_GET_CONNECTOR_MODES` and converts them with `gud_to_display_mode()`.

Property setup reads `GUD_REQ_GET_CONNECTOR_PROPERTIES`, creates matching DRM TV margin/mode/legacy TV properties, records initial values, and treats backlight brightness as a backlight property rather than a DRM property. During atomic check, TV property changes mark `connectors_changed` so `gud_pipe.c` can send a new device state. Backlight updates are queued on `system_long_wq`, build an atomic state that writes brightness into `connector_state->tv.brightness`, and commit outside the backlight lock.

## State And Persistence
Each connector persists its supported property IDs, initial TV state, initial brightness, current DRM connector state, optional backlight device, and encoder attachment. Runtime state changes are persisted in the DRM atomic state and later serialized into GUD property requests by `gud_connector_fill_properties()`. Device-side connector state is read or updated over USB control requests.

## Dependencies And Integration Points
The file depends on USB helpers from `gud_drv.c`, GUD protocol constants in `<drm/gud.h>`, mode conversion helpers in `gud_internal.h`, DRM connector/encoder/EDID/property helpers, backlight core, and `gud_pipe.c` atomic checking, which consumes property serialization.

## Risks
The protocol assumes connector indexes match DRM connector indexes; a mismatch returns `-EINVAL`. Invalid EDID sizes and malformed mode/property arrays are rejected, but unknown future properties are skipped, which can reduce functionality without failing probe. TV mode enum names are shared globally, so multiple connectors using TV mode must expose compatible names. Backlight updates perform asynchronous atomic commits and can fail after the backlight core has accepted a brightness change.

## Test Signals
Signals include correct connector count and type mapping from gadget descriptors, force-detect requests on forced probes, epoch increments on status changes, valid EDID and fallback mode enumeration, successful creation and reset of TV/backlight properties, `connectors_changed` on TV property updates, backlight sysfs updates resulting in GUD state commits, and clean connector destroy/early-unregister with no pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_connector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_drv.c

## Purpose
`gud_drv.c` is the Generic USB Display driver core. It owns USB probe/disconnect/power-management, protocol control transfers, display descriptor validation, DRM device and mode-config setup, format discovery and XRGB8888 emulation selection, bulk buffer allocation, plane/CRTC registration, connector discovery, debugfs statistics, and module registration.

## Important APIs, Types, And Functions
Internal DRM formats `gud_drm_format_r1` and `gud_drm_format_xrgb1111` describe protocol-only transfer formats. Exported internal USB helpers are `gud_usb_get()`, `gud_usb_set()`, `gud_usb_get_u8()`, and `gud_usb_set_u8()`. Major helpers include `gud_usb_control_msg()`, `gud_get_display_descriptor()`, `gud_status_to_errno()`, `gud_usb_get_status()`, `gud_usb_transfer()`, `gud_plane_add_properties()`, `gud_stats_debugfs()`, `gud_alloc_bulk_buffer()`, `gud_free_buffers_and_mutex()`, `gud_probe()`, `gud_disconnect()`, `gud_suspend()`, and `gud_resume()`.

The file defines the DRM callback tables for CRTC, plane, mode config, GEM fops, and `struct drm_driver`, and registers a USB driver with two vendor-specific USB IDs.

## Control Flow
Probe finds a bulk-out endpoint, reads and validates the GUD display descriptor, rejects unsupported protocol versions and inconsistent dimensions, allocates a managed `struct gud_device`, records flags/compression, initializes locks and flush work, sets USB interface data, optionally attaches the USB DMA device, initializes DRM mode config bounds, and discovers protocol formats through `GUD_REQ_GET_FORMATS`.

Supported protocol pixel formats are converted to DRM fourcc values. Internal R1 and XRGB1111 formats are kept for transfer conversion but not exposed to userspace. If the gadget lacks XRGB8888 but supports an emulatable lower-depth format, the driver exposes XRGB8888 to userspace and stores the emulation format for `gud_pipe.c`. It caps max bulk buffer size at 64 MiB, allocates a vmalloc buffer and scatterlist, allocates LZ4 memory if advertised, initializes a primary plane with damage clips, adds plane properties, creates one CRTC, discovers connectors, resets mode config, starts polling, adds debugfs stats, registers the DRM device, and starts DRM client setup.

USB control transfers are serialized by `ctrl_lock` and guarded by `drm_dev_enter()`. On control stalls or `STATUS_ON_SET` devices, `gud_usb_transfer()` reads `GUD_REQ_GET_STATUS` and maps protocol status codes to Linux errno values. Disconnect stops polling, unplugs the DRM device, and shuts down atomic state. Suspend and resume use DRM mode-config helper suspend/resume.

## State And Persistence
`struct gud_device` holds device flags, supported properties, bulk pipe and buffer metadata, compression buffers, transfer statistics, control and damage locks, and framebuffer damage state. Probe-created DRM objects persist until USB disconnect or device-managed cleanup. Debugfs reports max buffer size, error count, compression modes, and compression ratio derived from accumulated stats.

## Dependencies And Integration Points
The file depends on the USB core, DRM KMS/GEM shmem/fbdev/client helpers, LZ4, scatter-gather APIs, `<drm/gud.h>` protocol definitions, `gud_internal.h`, `gud_pipe.c` plane/CRTC helpers, and `gud_connector.c` connector discovery. Kconfig selects the needed helper libraries.

## Risks
The driver trusts the gadget enough to allocate buffers based on advertised dimensions and formats, mitigated by a 64 MiB cap. `GUD_DISPLAY_FLAG_FULL_UPDATE` is rejected with compression because the pipe path's full-update behavior conflicts with compressed rectangle metadata. `gud_usb_get_u8()` writes `*val` before checking transfer status, so callers must honor the return value. Misreported format lists can leave no exposed formats or force expensive emulation. Control transfers are synchronous and can block up to USB timeouts.

## Test Signals
Test probe with valid and malformed descriptors, unsupported protocol versions, missing bulk endpoints, empty/unknown format lists, XRGB8888 emulation paths, LZ4 and no-compression devices, plane rotation property discovery, connector discovery failure paths, debugfs stats after flushes, USB stall/status mapping, disconnect during active flush, and suspend/resume with active modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_internal.h

## Purpose
`gud_internal.h` defines the internal state and helper API shared by the Generic USB Display implementation files.

## Important APIs, Types, And Functions
The central type is `struct gud_device`, which embeds the DRM device, primary plane, CRTC, flush work, protocol flags, XRGB8888 emulation format, device property list, USB bulk transfer state, compression buffers, transfer statistics, control lock, damage lock, pending framebuffer/damage state, and optional shadow buffer.

It declares internal USB helpers, flush and atomic helpers, connector helpers, and the custom internal formats `GUD_DRM_FORMAT_R1` and `GUD_DRM_FORMAT_XRGB1111`. Inline helpers include `to_gud_device()`, `gud_to_usb_device()`, `gud_from_fourcc()`, `gud_to_fourcc()`, `gud_from_display_mode()`, and `gud_to_display_mode()`.

## Control Flow
The header has no standalone runtime flow, but its conversion helpers are in the active paths. Probe maps gadget pixel format IDs to DRM fourcc values with `gud_to_fourcc()`. Atomic state check maps the selected transfer format back with `gud_from_fourcc()`. Connector mode enumeration and atomic state serialization convert between DRM mode structures and little-endian GUD protocol mode structures.

## State And Persistence
All persistent driver-private state is described by `struct gud_device`. Control transfers are serialized by `ctrl_lock`; damage accumulation and async flushing are protected by `damage_lock`; `fb`, `damage`, `prev_flush_failed`, and `shadow_buf` persist between atomic updates and queued flush work.

## Dependencies And Integration Points
It depends on Linux list/mutex/scatterlist/USB/workqueue headers, DRM mode types, UAPI fourcc values, and protocol definitions from `<drm/gud.h>` included by the implementation files. It is the contract between `gud_drv.c`, `gud_pipe.c`, and `gud_connector.c`.

## Risks
Format conversion returns zero for unknown formats, so callers must reject zero before using it in protocol state. Mode conversion masks user-visible mode flags to `GUD_DISPLAY_MODE_FLAG_USER_MASK`, so unsupported future flags are intentionally dropped. The internal custom fourcc values must remain private and must not be exposed to userspace.

## Test Signals
Compile-time coverage across all three GUD C files is required. Runtime signals include correct protocol format mapping, correct preferred-mode flag round-trips, accurate connector property serialization, and absence of races between control transfers and asynchronous damage flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_pipe.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_pipe.c

## Purpose
`gud_pipe.c` implements the GUD primary plane and CRTC update path. It validates atomic state with the USB gadget, converts framebuffer damage rectangles into the gadget's selected transfer format, optionally compresses with LZ4, sends rectangle metadata over USB control transfers, transfers pixel data over USB bulk, and supports optional asynchronous damage coalescing.

## Important APIs, Types, And Functions
The module parameter `async_flush` enables queued flushing through `system_long_wq`. Public internal functions are `gud_clear_damage()`, `gud_flush_work()`, `gud_plane_atomic_check()`, `gud_crtc_atomic_enable()`, `gud_crtc_atomic_disable()`, and `gud_plane_atomic_update()`.

Important helpers include `gud_xrgb8888_to_r124()`, `gud_xrgb8888_to_color()`, `gud_prep_flush()`, `gud_usb_bulk_timeout()`, `gud_usb_bulk()`, `gud_flush_rect()`, `gud_flush_damage()`, `gud_fb_queue_damage()`, and `gud_fb_handle_damage()`. `struct gud_usb_bulk_context` holds the timer and USB scatter-gather request for one bulk transfer.

## Control Flow
Atomic check first validates plane scaling/visibility, marks mode changes for rotation or format changes, requires exactly one connector for visible state changes, resolves the active connector state, builds a `gud_state_req` containing display mode, transfer format, connector index, connector properties, and plane properties, then sends `GUD_REQ_SET_STATE_CHECK` to the gadget. CRTC enable sends controller enable, state commit, and display enable requests. Disable turns display and controller off.

Atomic update clears pending async damage and shadow buffers when the CRTC is disabled or mode-changed, enters the DRM device, begins CPU access to the framebuffer, iterates damage clips, and handles each damage rectangle. Full-update devices expand damage to the entire framebuffer. If async flushing is enabled, damage is copied to a shadow buffer, coalesced under `damage_lock`, and queued; otherwise flushing is synchronous.

Flush preparation chooses the actual transfer format, aligns sub-byte formats to byte boundaries, converts XRGB8888 to monochrome/gray/RGB332/RGB565/RGB888/XRGB1111 when needed, handles big-endian byte swapping, copies or directly references framebuffer data, fills `gud_set_buffer_req`, and tries LZ4 compression. If compression fails, it retries uncompressed. Large damage rectangles are split by the maximum bulk buffer length. Each rectangle may send `GUD_REQ_SET_BUFFER`, then performs a USB scatter-gather bulk transfer with a 3 second timeout.

## State And Persistence
State persists in `struct gud_device`: compression mode, bulk buffers and scatterlist, LZ4 memory, stats counters, `prev_flush_failed`, pending async `fb`, accumulated `damage`, and `shadow_buf`. `prev_flush_failed` causes the next full-update flush to resend buffer metadata. Transfer statistics accumulate uncompressed and actual byte counts for debugfs.

## Dependencies And Integration Points
The file depends on DRM atomic helpers, damage helpers, GEM framebuffer CPU access, format conversion helpers, LZ4, USB scatter-gather APIs, workqueues, GUD protocol requests, connector property serialization from `gud_connector_fill_properties()`, and USB control helpers from `gud_drv.c`.

## Risks
The file explicitly notes likely breakage on big-endian systems. If `bulk_len` is smaller than one line's pitch, the split calculation can produce zero lines, so descriptor/buffer sizing must prevent that. Async flushing trades latency for copied shadow memory and can coalesce damage beyond the original dirty rectangles. Imported buffers are treated as slow/uncached reads. USB bulk timeout cancellation and disconnect races rely on `drm_dev_enter()` and error filtering. Full-update plus compression is rejected at probe because this path cannot combine those semantics safely.

## Test Signals
Tests should exercise every supported and emulated pixel format, sub-byte rectangle alignment, LZ4 success and fallback, damage splitting at `bulk_len`, async and synchronous flushing, disconnect during active transfer, full-update devices, rotation state checks, connector property changes causing state checks, bulk timeout behavior, and debugfs compression/error counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/Kconfig

## Purpose
`hisilicon/Kconfig` is the top-level Kconfig include file for Hisilicon DRM drivers.

## Important APIs, Types, And Functions
It sources `drivers/gpu/drm/hisilicon/hibmc/Kconfig` and `drivers/gpu/drm/hisilicon/kirin/Kconfig`, with a comment requesting alphabetical ordering.

## Control Flow
There is no runtime flow. During kernel configuration, this file makes the HIBMC and Kirin DRM driver options visible under the Hisilicon DRM subtree.

## State And Persistence
The file stores build-time menu inclusion state only.

## Dependencies And Integration Points
It integrates with the DRM Kconfig hierarchy and delegates concrete options to child Kconfig files. In this work item, the relevant child is `hibmc/Kconfig`.

## Risks
Incorrect source paths or ordering mistakes can hide driver options from configuration. Adding new Hisilicon drivers requires updating this file.

## Test Signals
Kconfig tests should confirm `DRM_HISI_HIBMC` and Kirin options appear when the parent DRM menu is parsed and that all sourced paths exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/Makefile

## Purpose
`hisilicon/Makefile` routes configured Hisilicon DRM drivers into their subdirectories.

## Important APIs, Types, And Functions
It adds `hibmc/` when `CONFIG_DRM_HISI_HIBMC` is enabled and `kirin/` when `CONFIG_DRM_HISI_KIRIN` is enabled.

## Control Flow
There is no runtime flow. Kbuild uses these conditional object-directory entries to descend into driver-specific builds.

## State And Persistence
The file owns build graph state only.

## Dependencies And Integration Points
It connects the parent Hisilicon DRM directory to child makefiles such as `hibmc/Makefile`, where the `hibmc-drm` object composition is defined.

## Risks
If the symbol names diverge from child Kconfig options, the subdirectory will not build even when configured. Adding or renaming child drivers requires coordinated Kconfig and Makefile updates.

## Test Signals
Build tests should confirm enabling `CONFIG_DRM_HISI_HIBMC` descends into `hibmc/` and produces `hibmc-drm.o` or its module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/Kconfig

## Purpose
`hibmc/Kconfig` defines the kernel configuration option for the Hisilicon HIBMC DRM driver.

## Important APIs, Types, And Functions
It declares `config DRM_HISI_HIBMC` as a tristate option named "DRM Support for Hisilicon Hibmc". It depends on `DRM` and `PCI`, and selects `DRM_CLIENT_SELECTION`, `DRM_DISPLAY_HELPER`, `DRM_DISPLAY_DP_HELPER`, `DRM_KMS_HELPER`, `DRM_VRAM_HELPER`, `DRM_TTM`, `DRM_TTM_HELPER`, `I2C`, and `I2C_ALGOBIT`.

## Control Flow
There is no runtime flow. The option controls whether `hibmc/Makefile` builds the `hibmc-drm` driver as built-in or module.

## State And Persistence
The file stores build-time configuration state. When built as a module, the module is named `hibmc-drm`.

## Dependencies And Integration Points
The selected helpers match the driver tree's PCI device model, VRAM/TTM memory management, KMS helper use, DisplayPort AUX/link helpers, and I2C bit-banged VGA/DDC support.

## Risks
The option selects a broad set of DRM and I2C helpers; missing selections would break link or feature support in HIBMC display, DP, or VDAC/I2C code. PCI dependency means this option is not available for non-PCI HIBMC integration without Kconfig changes.

## Test Signals
Configuration and build tests should cover `CONFIG_DRM_HISI_HIBMC=y/m`, verify all selected helper symbols are enabled, and confirm the resulting module links all HIBMC core, DP, debugfs, VDAC, and I2C objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/Makefile

## Purpose
`hibmc/Makefile` defines the object composition for the Hisilicon HIBMC DRM driver.

## Important APIs, Types, And Functions
`hibmc-drm-y` links `hibmc_drm_drv.o`, `hibmc_drm_de.o`, `hibmc_drm_vdac.o`, `hibmc_drm_i2c.o`, DisplayPort objects `dp/dp_aux.o`, `dp/dp_link.o`, `dp/dp_hw.o`, `dp/dp_serdes.o`, the wrapper `hibmc_drm_dp.o`, and `hibmc_drm_debugfs.o`. `obj-$(CONFIG_DRM_HISI_HIBMC)` emits `hibmc-drm.o`.

## Control Flow
There is no runtime control flow. Kbuild links the display engine, analog output, I2C, DP AUX/link/hardware/serdes, top-level DP integration, debugfs, and PCI/DRM core into one module or built-in object.

## State And Persistence
The file owns build graph state only.

## Dependencies And Integration Points
It ties the DP AUX file in this work item to the rest of the HIBMC DP implementation and the main HIBMC DRM driver. Any new HIBMC source file must be added here to participate in the final driver.

## Risks
Missing an object can produce unresolved symbols or disable an output path. Since DP files are linked into the main HIBMC module, DP build failures prevent the whole driver from building.

## Test Signals
Build `CONFIG_DRM_HISI_HIBMC=m` and verify `hibmc-drm.ko` contains the listed DP, display engine, VDAC, I2C, and debugfs units with no unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_aux.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_aux.c

## Purpose
`dp_aux.c` implements the DisplayPort AUX transfer backend for the Hisilicon HIBMC DRM driver. It programs HIBMC DP AUX registers, marshals AUX request data, waits for transfer completion, parses hardware status, exposes a `drm_dp_aux` transfer callback, and initializes AUX timing fields.

## Important APIs, Types, And Functions
The public function is `hibmc_dp_aux_init(struct hibmc_dp *dp)`. Internal helpers include `hibmc_dp_aux_reset()`, `hibmc_dp_aux_read_data()`, `hibmc_dp_aux_write_data()`, `hibmc_dp_aux_build_cmd()`, `hibmc_dp_aux_parse_xfer()`, and `hibmc_dp_aux_xfer()`.

Important bitfields are `HIBMC_AUX_CMD_REQ_LEN`, `HIBMC_AUX_CMD_ADDR`, `HIBMC_AUX_CMD_I2C_ADDR_ONLY`, `HIBMC_AUX_I2C_WRITE_SUCCESS`, and `HIBMC_DP_MIN_PULSE_NUM`. The code uses DP core request/reply constants such as `DP_AUX_NATIVE_WRITE`, `DP_AUX_NATIVE_READ`, `DP_AUX_I2C_WRITE | DP_AUX_I2C_MOT`, `DP_AUX_I2C_READ | DP_AUX_I2C_MOT`, and `DP_AUX_NATIVE_REPLY_ACK`.

## Control Flow
For each transfer, `hibmc_dp_aux_xfer()` clears the four AUX write-data registers, writes request bytes into little-endian 32-bit write-data registers, builds the command word from request type, payload length or address-only flag, and AUX address, writes it to `HIBMC_DP_AUX_CMD_ADDR`, asserts `HIBMC_DP_CFG_AUX_REQ`, and polls the request bit for completion at 50 microsecond intervals up to 5 milliseconds. On timeout it resets the AUX block and returns the poll error. On completion it calls `hibmc_dp_aux_parse_xfer()`.

Parsing reads `HIBMC_DP_AUX_STATUS`, stores the hardware reply in `msg->reply`, reports `-ETIMEDOUT` for hardware timeout, returns 0 for address-only requests, rejects non-ACK replies for data transfers, returns full size for native writes, validates I2C write success through the ready-byte count, validates read byte count, copies read registers into the caller buffer for successful reads, and returns `-EINVAL` for unsupported request types.

Initialization programs AUX sync length, timer timeout, and minimum pulse count fields, assigns the transfer callback, name, DRM device, calls `drm_dp_aux_init()`, and stores the AUX pointer in `dp_dev`.

## State And Persistence
Hardware state includes AUX reset, request, command/address, write-data, read-data, status, timing, and pulse-width registers. Software state is stored in `struct hibmc_dp`'s `drm_dp_aux` and `struct hibmc_dp_dev`'s `aux` pointer. AUX register writes persist until reconfigured or hardware reset.

## Dependencies And Integration Points
The file depends on `dp_comm.h` for `struct hibmc_dp_dev` and the register-field write macro, `dp_reg.h` for HIBMC DP register offsets and masks, `dp_hw.h` for the enclosing `struct hibmc_dp`, Linux MMIO and polling helpers, and DRM DP AUX helpers. It feeds DPCD, EDID-over-AUX, link training, and downstream port discovery in the rest of the HIBMC DP stack.

## Risks
Only a subset of AUX request encodings is accepted; callers using non-MOT I2C requests or other variants may get `-EINVAL`. The read path decrements the ready-byte count before comparing with `msg->size`, so hardware status semantics must match that expectation. AUX write-data and read-data are packed little-endian into 32-bit registers. Poll timeout triggers an AUX reset, which can disrupt concurrent or immediately following transactions. The register-field macro uses a mutex, but raw data register writes in this file are not individually locked.

## Test Signals
Useful tests include DPCD native reads/writes during link training, EDID reads over AUX I2C with MOT, address-only I2C probes, hardware timeout recovery and subsequent successful transfer, malformed reply handling, partial read count returning `-EBUSY`, and successful `drm_dp_aux` registration visible to DRM DP helper users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_comm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_comm.h

## Purpose
`dp_comm.h` defines common DisplayPort data structures, limits, register-field helpers, and cross-file function prototypes for the HIBMC DP implementation.

## Important APIs, Types, And Functions
The file defines `HIBMC_DP_LANE_NUM_MAX` as 2, `struct hibmc_link_status`, `struct hibmc_link_cap`, `struct hibmc_dp_link`, and `struct hibmc_dp_dev`. `struct hibmc_dp_dev` stores the `drm_dp_aux`, DRM device, MMIO base, register mutex, link-training state, DPCD buffer, downstream port buffer, DP descriptor, branch-device flag, HPD status, and serdes base.

Macros include `dp_field_modify(reg_value, mask, val)` and `hibmc_dp_reg_write_field(dp, offset, mask, val)`, the latter performing a mutex-protected read/modify/write using `FIELD_PREP`. Prototypes expose `hibmc_dp_aux_init()`, `hibmc_dp_link_training()`, `hibmc_dp_serdes_init()`, `hibmc_dp_serdes_rate_switch()`, and `hibmc_dp_serdes_set_tx_cfg()`.

## Control Flow
The header itself has no executable flow, but `hibmc_dp_reg_write_field()` expands into a locked read/modify/write sequence. DP implementation files use the shared structures to coordinate AUX initialization, link training, serdes setup, rate changes, and TX configuration.

## State And Persistence
`struct hibmc_dp_dev` is the persistent DP hardware context. It caches DPCD capabilities, downstream port information, link capabilities, training set values, HPD status, MMIO bases, and the AUX pointer. The mutex protects concurrent register-field updates through the macro.

## Dependencies And Integration Points
It depends on Linux bitfield, mutex, MMIO, errno, and type headers, plus DRM DP helper definitions and `dp_hw.h`. It is included by `dp_aux.c` and the other DP implementation files in the HIBMC driver.

## Risks
The register write macro evaluates the `dp` expression once but assumes a valid initialized mutex and MMIO base. It only protects accesses made through the macro; direct `readl()`/`writel()` sequences elsewhere must handle ordering and concurrency separately. Lane count is hard-limited to 2, so higher-lane hardware would require structural changes.

## Test Signals
Build coverage across all DP files, lockdep-clean concurrent register updates, successful two-lane and one-lane link training, correct DPCD cache population, and serdes rate/voltage/pre-emphasis changes reflected in hardware are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_comm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_config.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_config.h

## Purpose
`dp_config.h` centralizes fixed HIBMC DisplayPort configuration constants used by the DP hardware, link, and mode-validation code.

## Important APIs, Types, And Functions
The file defines constants for bits per pixel (`HIBMC_DP_BPP`), symbols per fclk, MSA register defaults, DP register offset, HDCP selector, interrupt/reset masks, clock enable mask, sync enable mask, link-rate calculation factor, sync delay based on lane count, interrupt enable mask, and `DP_MODE_VALI_CAL`.

## Control Flow
There is no executable flow. The only expression-like macro is `HIBMC_DP_SYNC_DELAY(lanes)`, which selects a delay value of 86 for two lanes and 46 otherwise.

## State And Persistence
The file owns no state. The constants are written into or compared against DP hardware configuration by other HIBMC DP files.

## Dependencies And Integration Points
It is part of the HIBMC DP support set and complements `dp_comm.h`, `dp_reg.h`, `dp_hw.c`, `dp_link.c`, and `hibmc_drm_dp.c`. The mode-validation calculation constant is tied to a comment that `HIBMC_DP_LINK_RATE_CAL * 10000 * 80% = 216000`.

## Risks
Hard-coded constants imply a specific HIBMC DP hardware profile: 24 bpp, maximum two-lane behavior, fixed masks, and fixed validation margin. New hardware revisions or different lane rates may require updates. `HIBMC_DP_SYNC_DELAY(lanes)` treats every non-2 lane count the same.

## Test Signals
Validate DP modes at expected bandwidth limits, one-lane and two-lane sync timing, reset/clock/interrupt bring-up, MSA programming, and regression tests for mode validation around the `DP_MODE_VALI_CAL` threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_config.h -->

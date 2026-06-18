# subset-b-003664 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp5.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp5.xml

## Purpose
This XML file is a Freedreno/Nouveau RNN register database for Qualcomm MDP5 display hardware. It imports shared display definitions from `display/mdp_common.xml` and copyright metadata, then describes the `MDP5` 32-bit register domain plus an empty `VBIF` placeholder. Its output is consumed by `gen_header.py` and related register-generation tooling to produce C register offsets, bit masks, enum values, and pack helpers used by the MSM DRM display driver.

## Important APIs, Types, And Data
The file defines display-facing enums such as `mdp5_intf_type`, `mdp5_intfnum`, `mdp5_pipe`, `mdp5_ctl_mode`, scale filters, cursor formats, writeback modes, and color/rotation enums. `MDP5_IRQ` models interrupt bits for writeback, ping-pong completion/read/write/auto-refresh, underrun, and vsync. Register arrays model hardware blocks: global `SMP_ALLOC_*`, `IGC`, `CTL`, `PIPE`, `LM`, `DSPP`, `PP`, `WB`, `INTF`, and `AD`. Several arrays use `doffsets` expressions such as `mdp5_cfg->pipe_vig.base[0]`, so generated accessors depend on runtime MDP5 configuration tables rather than hard-coded offsets alone.

## Control Flow, State, And Integration
There is no executable flow in the XML itself. The effective flow is parser-driven: imports are resolved, enums and bitsets are registered, then arrays/regs become generated `REG_MDP5_*` accessors and field macros. State represented here is volatile hardware state: scanout source addresses, layer mixer composition, control flush bits, timing generator settings, color-space conversion coefficients, cursor configuration, writeback destination addresses, SMP allocation, and interrupt status/enable/clear. Integration points are the MSM DRM MDP5 KMS path and generated headers expected by code that programs MDP5 blocks.

## Risks And Test Signals
The largest risks are incorrect offsets/bit positions and stale hardware assumptions. Comments mark uncertain areas, including IGC disable bits, CTL layer extension compatibility, `mdp5_format` as a TODO, and a `VBIF` placement question. Dynamic offsets must stay in sync with `mdp5_cfg` structures. Test signals are successful header generation, schema validation, successful MSM display modesets, no underrun/vsync IRQ regressions, cursor/writeback tests, and register traces matching downstream or hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp5.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp_common.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp_common.xml

## Purpose
This XML file holds shared RNN definitions used by Qualcomm MDP display register databases. It avoids duplicating common pixel-format, component, alpha, fetch, coordinate, and packing definitions between MDP generations, especially MDP4 and MDP5.

## Important APIs, Types, And Data
The key exported enums are `mdp_chroma_samp_type`, `mdp_fetch_type`, `mdp_mixer_stage_id`, `mdp_alpha_type`, `mdp_component_type`, `mdp_bpc`, `mdp_bpc_alpha`, and `mdp_fetch_mode`. Inline bitsets `reg_wh` and `reg_xy` encode common 16-bit width/height and x/y register layouts. `mdp_unpack_pattern` defines four 8-bit unpack elements for source pixel unpack registers. These types are referenced by `mdp5.xml` fields such as `SRC_SIZE`, `SRC_XY`, `SRC_FORMAT`, `SRC_UNPACK`, blending controls, and pixel extension arrays.

## Control Flow, State, And Integration
The file has no runtime execution. During generation, `gen_header.py` imports it first, registers its enums and inline bitsets, and lets later files use them as field types. The state described is reusable hardware register encoding, not persistent driver state. Because inline bitsets are expanded into register-specific macros, changes here affect every imported register database that references the shared names.

## Risks And Test Signals
Any enum value drift can silently corrupt generated field programming across multiple display generations. The risk is high for `mdp_mixer_stage_id` because stage IDs encode z-order and are split across legacy low bits and MDP5 extension bits. Test signals include successful RNN parsing, no unknown-type errors when generating MDP headers, generated macros matching expected names, and display composition tests that exercise scaling, alpha blending, YUV formats, and source unpacking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp_common.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdss.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdss.xml

## Purpose
This XML file describes the top-level Qualcomm MDSS register block used around the MDP/display subsystem. It is a small RNN database focused on MDSS hardware version, interrupt summary, and UBWC static/control registers.

## Important APIs, Types, And Data
The `MDSS` 32-bit domain defines `HW_VERSION` with `STEP`, `MINOR`, and `MAJOR` fields. `HW_INTR_STATUS` exposes summary bits for MDP, DSI0, DSI1, HDMI, and eDP interrupts. UBWC registers include `UBWC_DEC_HW_VERSION`, `UBWC_STATIC`, `UBWC_CTRL_2`, and `UBWC_PREDICTION_MODE`; `UBWC_STATIC` encodes swizzle, bank spread, highest bank bit, min access length, AMSBC, and macrotile mode.

## Control Flow, State, And Integration
Generation converts these descriptions into accessors used by MSM display code to identify MDSS revisions, route top-level interrupts, and configure UBWC-related display memory behavior. The file models volatile SoC-global display state. It integrates with generated display headers rather than directly with C source.

## Risks And Test Signals
The `HIGHEST_BANK_BIT` comment notes that older UBWC revisions used a narrower field, so version-specific programming must interpret the generated macro correctly. Incorrect interrupt bits would break display IRQ demultiplexing. Test signals include generated headers compiling, MDSS version reads matching hardware, DSI/HDMI/eDP interrupt handling working, and UBWC framebuffers scanning out without corruption across supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdss.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/msm.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/msm.xml

## Purpose
This XML file is an aggregate RNN database for display-related MSM/Snapdragon hardware blocks. It imports the copyright metadata and then includes individual block descriptions for MDP, DSI, DSI PHY generations, SFPB, HDMI, and eDP.

## Important APIs, Types, And Data
The file does not define registers directly. Its important data is the import manifest: `mdp4.xml`, `mdp5.xml`, `dsi.xml`, DSI PHY files for 28nm/20nm/14nm/10nm/7nm, `sfpb.xml`, `hdmi.xml`, and `edp.xml`. The `<doc>` node identifies the database as display hardware register definitions for `msm/snapdragon`.

## Control Flow, State, And Integration
The generator parses this as a top-level entry point. Import order matters because earlier files can provide shared types and domains that later files reference. The state represented by the resulting generated headers spans many display hardware blocks. This file integrates the smaller per-block XML files into a single display register-generation unit.

## Risks And Test Signals
The main risk is broken relative imports or schema drift. The schema location differs from several newer files (`rules-ng.xsd` URL rather than `rules-fd.xsd`), so validation behavior may differ depending on available schema files. Test signals are full display header generation from this aggregate file, no duplicate/unknown type failures, and successful compile of MSM display code using the generated combined definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/msm.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/sfpb.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/sfpb.xml

## Purpose
This RNN XML describes the small SFPB display-adjacent register block used for AHB arbitration/master-port control.

## Important APIs, Types, And Data
The `SFPB` 32-bit domain defines enum `sfpb_ahb_arb_master_port_en` with `SFPB_MASTER_PORT_ENABLE` value `3` and `SFPB_MASTER_PORT_DISABLE` value `0`. Register `GPREG` at offset `0x0058` exposes field `MASTER_PORT_EN` in bits 11:12 using that enum.

## Control Flow, State, And Integration
There is no executable code. Generation produces register and field helpers for SFPB programming. Runtime state is limited to the master-port-enable bits in `GPREG`, which likely gate or arbitrate a bus master path needed by display hardware. The file is imported by `msm.xml`.

## Risks And Test Signals
Because this is a tiny hardware-control file, the principal risks are wrong bit positions or misuse of an enum that requires a two-bit value rather than a boolean. Test signals are generated macro correctness, display initialization sequences that program SFPB without bus faults, and hardware validation that enable/disable values actually affect the expected master port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/sfpb.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/freedreno_copyright.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/freedreno_copyright.xml

## Purpose
This XML file centralizes copyright, author, and MIT license metadata for Freedreno RNN register database files.

## Important APIs, Types, And Data
It defines a `<copyright year="2013">` element with authors Rob Clark and Ilia Mirkin and embeds the MIT license text. Files such as `mdp5.xml`, `mdp_common.xml`, `mdss.xml`, and `sfpb.xml` import it so generated or processed documentation can preserve attribution and licensing consistently.

## Control Flow, State, And Integration
The file has no register state or runtime behavior. During XML parsing, it is imported once per parser instance and de-duplicated by `gen_header.py` through absolute-file tracking. It is metadata input to the register-generation ecosystem rather than kernel runtime code.

## Risks And Test Signals
Risk is mostly compliance-related: if imports are removed or parsing ignores copyright nodes in downstream tooling, generated artifacts may lose attribution. The XML must remain schema-compatible with the RNN rules file. Test signals are successful import parsing, generated headers retaining the intended license banner from generator code, and repository license checks continuing to identify the register database as MIT-licensed metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/freedreno_copyright.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/gen_header.py -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/gen_header.py

## Purpose
`gen_header.py` is the Python generator that parses RNN XML register databases and emits C register defines, C pack-struct helpers, or Python enum-style register offsets. It is used by the Freedreno/MSM register definition workflow to convert XML domains, arrays, bitsets, fields, and variants into typed helper code.

## Important APIs, Types, And Functions
Core model classes are `Enum`, `Field`, `Bitset`, `Array`, `Reg`, and `Parser`. `Field` validates bit ranges and builtin/custom types, and its `ctype()` maps XML field types to C field types and conversion expressions. `Bitset.dump()` emits masks, shifts, booleans, and inline builder functions; `dump_pack_struct()` emits `struct fd_reg_pair` pack helpers with debug assertions. `Array` handles fixed offsets, dynamic offsets (`doffsets`), indexed arrays, nested arrays, and generated offset switch functions. `Reg.dump()` emits `REG_*` macros or inline functions. `Parser` handles expat callbacks, imports, schema validation through optional `lxml`, variant/use tracking, and output collection. CLI subcommands are `c-defines`, `c-pack-structs`, and `py-defines`.

## Control Flow, State, And Integration
`main()` parses `--rnn`, `--xml`, validation flags, and subcommand, then calls the selected dumper. `Parser.parse()` initializes stack and validation state, recursively parses imports with duplicate suppression, and builds `self.file`, `self.enums`, `self.bitsets`, `self.variant_regs`, and usage maps. Generation prints directly to stdout. Persistent state is not written; all parser state is process-local. Integration points are XML register files, RNN schema files, C/C++ compiler consumers, `fd_reg_pair` users, and Python tooling that can consume generated `IntEnum` classes.

## Risks And Test Signals
Risks include stdout-only generation failures, import path mistakes, optional validation silently skipped without `lxml`, fixed-offset switch names colliding for repeated local array names, and variant handling that explicitly notes TODO coverage gaps for open-ended/all variants. Address fields carry buffer-object metadata, so incorrect `waddress` handling can affect relocation semantics. Test signals include running all subcommands on representative XML, schema validation when `lxml` exists, compiling generated headers in C and C++, assertions catching oversized field values, and comparing generated offsets against known hardware traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/gen_header.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/Kconfig

## Purpose
This Kconfig file declares build-time configuration for the MXS/LCDIF DRM drivers. It separates a common internal selector, the classic i.MX `(e)LCDIF` controller driver, and the newer i.MX LCDIFv3 driver.

## Important APIs, Types, And Data
`config DRM_MXS` is a hidden boolean selected by the concrete drivers. `config DRM_MXSFB` is a tristate for i.MX23, i.MX28, i.MX6SX, i.MX7, and i.MX8M LCDIF/eLCDIF hardware and builds module `mxsfb`. `config DRM_IMX_LCDIF` is a tristate for LCDIFv3 hardware on i.MX8MP and i.MXRT-class SoCs and builds module `imx-lcdif`. Both depend on DRM, OF, COMMON_CLK, and relevant architecture/compile-test support, and both select DRM client setup, KMS helper, DMA GEM helper, panel, and panel bridge support.

## Control Flow, State, And Integration
The file controls Kbuild inclusion and dependency closure rather than runtime behavior. Enabling either driver brings in the required DRM helpers and panel bridge support needed by probe paths in `mxsfb_drv.c` and `lcdif_drv.c`.

## Risks And Test Signals
Dependency mistakes can cause link failures or missing runtime helpers. The broad `COMPILE_TEST` path should catch portability issues, while architecture dependencies prevent irrelevant prompts on most systems. Test signals are `oldconfig/menuconfig` visibility, allmodconfig/allyesconfig builds, module names matching help text, and successful probe on device trees using compatible strings handled by the C drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/Makefile

## Purpose
This Makefile maps the Kconfig symbols in the `mxsfb` directory to kernel objects.

## Important APIs, Types, And Data
`mxsfb-y` combines `mxsfb_drv.o` and `mxsfb_kms.o`; `obj-$(CONFIG_DRM_MXSFB)` links them as `mxsfb.o`. `imx-lcdif-y` combines `lcdif_drv.o` and `lcdif_kms.o`; `obj-$(CONFIG_DRM_IMX_LCDIF)` links them as `imx-lcdif.o`.

## Control Flow, State, And Integration
There is no runtime control flow. Kbuild uses the variables to compile the platform-driver/probe portions and KMS plane/CRTC portions together for each hardware generation. The module split mirrors the source split between classic LCDIF and LCDIFv3.

## Risks And Test Signals
The main risk is object omission: missing the KMS object would leave unresolved `*_kms_init`, while missing the driver object would omit module registration. Test signals are successful module builds for `CONFIG_DRM_MXSFB=m/y` and `CONFIG_DRM_IMX_LCDIF=m/y`, plus modpost showing the expected module names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_drv.c

## Purpose
`lcdif_drv.c` is the platform-driver and DRM-device setup for the i.MX LCDIFv3 controller (`imx-lcdif`). It allocates the DRM device, maps registers, obtains clocks, initializes KMS objects, attaches output bridges, installs IRQ handling, and wires runtime/system PM.

## Important APIs, Types, And Functions
Important entry points are `lcdif_probe`, `lcdif_remove`, `lcdif_shutdown`, `lcdif_load`, `lcdif_unload`, `lcdif_irq_handler`, runtime PM callbacks, and system suspend/resume callbacks. The file defines `lcdif_driver` with GEM DMA and fbdev DMA ops, `lcdif_mode_config_funcs`, `lcdif_mode_config_helpers` using `drm_atomic_helper_commit_tail_rpm`, and a simple encoder destroy callback. Device-tree matches are `fsl,imx8mp-lcdif` and `fsl,imx93-lcdif`.

## Control Flow, State, And Integration
Probe allocates `drm_device`, calls `lcdif_load`, registers DRM, then starts DRM client setup. `lcdif_load` allocates `struct lcdif_drm_private`, maps MMIO, gets `pix`, `axi`, and `disp_axi` clocks, sets a 36-bit coherent DMA mask, initializes mode config, calls `lcdif_kms_init`, initializes vblank, attaches one encoder/bridge per OF endpoint, configures dimensions and helper callbacks, requests IRQ, starts polling, and enables runtime PM. The IRQ reads `LCDC_V8_INT_STATUS_D0`, handles vblank only when `VS_BLANK` is set and `SHADOW_LOAD_EN` is clear, then acknowledges status.

## State, Dependencies, And Risks
State lives in `drm->dev_private`: MMIO base, clocks, IRQ, DRM objects, and primary plane/CRTC. Runtime PM owns the clock-enable order: AXI, display AXI, pixel clock on resume and reverse on suspend. Risks include bridge endpoint parsing failures, missed vblank when shadow load is pending, unchecked `clk_prepare_enable()` errors in runtime resume, and PM imbalance if load/unload error paths change. Test signals include DT probe, bridge attach, atomic modeset, vblank wait/page flip behavior, suspend/resume, and interrupt storm absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_drv.h

## Purpose
This header defines the private driver state and KMS initialization contract for the LCDIFv3 DRM driver.

## Important APIs, Types, And Data
`struct lcdif_drm_private` stores the MMIO `base`, three clocks (`clk`, `clk_axi`, `clk_disp_axi`), IRQ number, back-pointer to `struct drm_device`, a primary plane, and one CRTC. `to_lcdif_drm_private()` returns `drm->dev_private`, and `lcdif_kms_init()` is declared for the driver setup file.

## Control Flow, State, And Integration
The header is shared by `lcdif_drv.c` and `lcdif_kms.c`. `lcdif_drv.c` allocates and fills the structure, while `lcdif_kms.c` consumes it for register programming, plane setup, vblank control, and atomic CRTC operations. State is not persistent across unload; it is devm/kzalloc-backed runtime driver state.

## Risks And Test Signals
Because this is the central private-state contract, field layout changes affect both driver and KMS files. The comment notes i.MXRT overlay-plane support is not implemented yet, so assumptions of a single primary plane are embedded in current code. Test signals are clean compilation, successful `drm->dev_private` casts, and KMS init paths finding initialized MMIO and clock fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_kms.c

## Purpose
`lcdif_kms.c` implements the LCDIFv3 KMS pipeline: primary plane validation/update, CRTC atomic state, mode programming, colorspace conversion, buffer-address programming, vblank control, and CRTC/plane registration.

## Important APIs, Types, And Functions
`struct lcdif_crtc_state` extends `drm_crtc_state` with bridge-selected `bus_format` and `bus_flags`. Key functions are `lcdif_set_formats`, `lcdif_set_mode`, `lcdif_enable_controller`, `lcdif_disable_controller`, `lcdif_reset_block`, `lcdif_crtc_atomic_check`, `lcdif_crtc_atomic_flush`, `lcdif_crtc_atomic_enable`, `lcdif_crtc_atomic_disable`, vblank enable/disable helpers, primary-plane `atomic_check`/`atomic_update`, and `lcdif_kms_init`. Supported primary formats include RGB565/RGB888/XRGB variants and packed YCbCr formats; only linear modifiers are accepted. Plane color properties support BT.601, BT.709, BT.2020 and limited/full range.

## Control Flow, State, And Integration
Atomic check requires the primary plane when the CRTC is active and derives a consistent input bus format/flags from connected bridge state. Enable sets the pixel clock, resumes runtime PM, resets the hardware, programs bus/pixel format and CSC coefficients, writes timing and pitch registers, writes the initial DMA address to low/high descriptor registers, enables FIFO panic priority boosting, turns on display and descriptor enable, then enables vblank. Flush sets `SHADOW_LOAD_EN` and arms or sends pending vblank events. Disable turns vblank off, disables the controller with a poll, sends any pending event, and drops runtime PM.

## State, Dependencies, Risks, And Tests
State is volatile MMIO plus atomic CRTC state. Dependencies include DRM atomic helpers, bridge bus-format negotiation, DMA GEM helpers, media bus formats, runtime PM, and `lcdif_regs.h` macros. Risks include unknown bridge formats falling back to RGB888, CSC coefficient mistakes, a disabled primary plane on active CRTC, timeout disabling the controller, and address handling relying on the 36-bit DMA mask. Test signals are atomic modeset/page-flip tests, YUV-to-RGB/RGB-to-YCbCr visual validation, vblank event timing, suspend/resume, and underrun/panic behavior under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_regs.h

## Purpose
This header defines LCDIFv3 register offsets and bitfield macros, plus some legacy LCDIF definitions retained in the shared directory. It is the low-level programming vocabulary for `lcdif_kms.c`.

## Important APIs, Types, And Data
LCDIFv3 offsets include `LCDC_V8_CTRL`, display parameters/size/sync registers, interrupt status/enable banks, descriptor registers, CSC coefficient registers, and panic threshold. Macros encode control polarity/reset bits, line patterns, display size, hsync/vsync porch/width fields, interrupt bits, descriptor size/pitch/address/high bits, BPP/YUV formats, CSC modes and coefficients, panic watermarks, and min/max resolutions. `REG_SET` and `REG_CLR` express the hardware set/clear alias offsets.

## Control Flow, State, And Integration
The header has no executable flow. It is included by the LCDIFv3 driver and KMS files to construct values for MMIO writes. The state described is entirely hardware register state: timing, pixel format, DMA address, interrupt masking/status, CSC matrix, and FIFO panic thresholds.

## Risks And Test Signals
Bitfield helper macros do not use `FIELD_PREP` consistently, so wrong masks or shifts can truncate values quietly. Some older non-v8 definitions coexist in the file; users must select the correct register set. Test signals include build coverage, register traces for programmed modes, visual tests for RGB/YUV formats, vblank IRQ behavior, and successful scanout at maximum supported pitch/address ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_drv.c

## Purpose
`mxsfb_drv.c` is the platform-driver and DRM setup for classic MXS/i.MX LCDIF/eLCDIF controllers. It handles device matching, SoC capability data, DRM allocation/registration, bridge attachment, IRQ installation, fb creation policy, and suspend/resume.

## Important APIs, Types, And Functions
The file defines `enum mxsfb_devtype` and `mxsfb_devdata[]` for V3, V4, and V6 register/capability differences: transfer-count/current/next-buffer offsets, hsync width encoding, overlay, CTRL2, and CRC32 support. Key functions are `mxsfb_probe`, `mxsfb_remove`, `mxsfb_shutdown`, `mxsfb_load`, `mxsfb_unload`, `mxsfb_attach_bridge`, IRQ helpers, and AXI clock wrappers. `mxsfb_fb_create()` rejects framebuffers whose pitch is not exactly width times bytes-per-pixel, matching hardware constraints.

## Control Flow, State, And Integration
Probe allocates a DRM device, loads private state based on `device_get_match_data`, removes conflicting framebuffers, registers the DRM device, and starts client setup. Load maps MMIO, gets clocks, sets a 32-bit DMA mask, enables runtime PM, initializes mode config and KMS, initializes vblank, attaches a panel/bridge, sets mode limits, requests IRQ under runtime PM, initializes polling, and stores driver data. The IRQ reads `LCDC_CTRL1`, handles frame-done vblank, optionally records CRC32 entries, clears the frame-done IRQ, and returns handled.

## State, Dependencies, Risks, And Tests
Private state holds devdata, MMIO, clocks, IRQ, CRTC/planes/encoder/connector/bridge, and `crc_active`. Dependencies include DRM GEM DMA, panel bridge, OF graph helpers, aperture conflict removal, PM runtime, and KMS code in `mxsfb_kms.c`. Risks include strict pitch rejection surprising userspace, connector acquisition as a documented bridge-API hack, IRQ cleanup requiring runtime clocks, and returning from `mxsfb_probe` without `drm_dev_put()` if aperture removal fails. Test signals include all compatible DT probes, simplefb handoff, vblank/CRC tests, panel bridge modesets, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_drv.h

## Purpose
This header defines the private data model and exported helper functions for the classic MXSFB DRM driver.

## Important APIs, Types, And Data
`struct mxsfb_devdata` captures hardware-generation differences: register offsets for transfer count/current/next buffer, hsync width mask/shift, and booleans for overlay, CTRL2, and CRC32 support. `struct mxsfb_drm_private` stores devdata, MMIO, clocks, IRQ, DRM objects, primary/overlay planes, CRTC, encoder, connector, bridge, and CRC active state. It declares AXI clock helpers and `mxsfb_kms_init()`.

## Control Flow, State, And Integration
The header is the state contract between `mxsfb_drv.c` and `mxsfb_kms.c`. The probe path initializes fields; KMS code reads devdata to choose offsets and optional features. No persistence exists outside the live device instance.

## Risks And Test Signals
Incorrect devdata values affect all register programming paths. Optional fields such as `clk_disp_axi`, overlay plane, and CRC support require KMS and driver code to branch consistently. Test signals are successful compile, correct SoC match data, mode setting on V3/V4/V6 hardware, overlay initialization only where supported, and CRC source availability only on CRC-capable variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_kms.c

## Purpose
`mxsfb_kms.c` implements KMS for classic MXS/i.MX LCDIF controllers: CRTC mode programming, controller reset/enable/disable, primary and optional overlay planes, vblank, CRC capture, and encoder/CRTC registration.

## Important APIs, Types, And Functions
Important functions include `mxsfb_set_formats`, `mxsfb_set_mode`, `mxsfb_enable_controller`, `mxsfb_disable_controller`, `mxsfb_reset_block`, `mxsfb_crtc_mode_set_nofb`, atomic CRTC enable/disable/flush/check helpers, vblank enable/disable, CRC source callbacks, primary/overlay plane updates, and `mxsfb_kms_init`. Supported primary formats are RGB565 and XRGB8888; overlay formats include XRGB/ARGB 4444, 1555, RGB565, XRGB8888, and ARGB8888. Only linear modifiers are supported.

## Control Flow, State, And Integration
Enable resumes runtime PM, enables AXI, turns vblank on, chooses a bridge or connector bus format with RGB888 fallback, resets the block, programs format/timing/clock, writes current and next buffer addresses, then starts the controller. Mode programming writes transfer count, VDCTRL timing registers, bus polarity, dotclock edge, and valid-data count. Controller enable turns on display clocks, sets outstanding requests on newer IP, enables sync signals, sets underflow recovery, and starts DMA. Disable stops dotclock mode, polls for `CTRL_RUN` clear, disables sync signals and clocks, sends pending events, turns vblank off, disables AXI, and drops runtime PM.

## State, Dependencies, Risks, And Tests
State includes MMIO registers, devdata-specific offsets, runtime clocks, optional overlay registers, and `crc_active`. Dependencies include DRM atomic helpers, panel/bridge bus metadata, DMA GEM helpers, PM runtime, and `mxsfb_regs.h`. Risks include ignored reset errors beyond an early return from mode programming, fallback bus formats, the overlay 64-byte DMA offset hack, no scaling support, strict linear layout, and underflow recovery relying on undocumented behavior. Test signals are primary/overlay plane tests, vblank/page-flip timing, CRC readout, reset/enable/disable under repeated modesets, and hardware tests on V3/V4/V6 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_regs.h

## Purpose
This header defines register offsets and bitfield macros for classic MXS/i.MX LCDIF/eLCDIF display controllers.

## Important APIs, Types, And Data
Offsets cover `LCDC_CTRL`, `CTRL1`, V3/V4 transfer count/current/next buffers, VDCTRL timing registers, CRC/debug registers, and overlay `AS_*` registers. Macros encode reset/clock-gate/run bits, bus width, word length, byte packaging, frame-done IRQ bits, CTRL2 outstanding request settings, transfer dimensions, sync polarity/width/period, wait counts, valid-data count, debug sync bits, overlay alpha/format/color-key/enable fields, and min/max resolution.

## Control Flow, State, And Integration
The file is a macro-only hardware contract consumed by `mxsfb_drv.c` and `mxsfb_kms.c`. The KMS path combines these macros with mode, format, and SoC devdata to program volatile controller state. `REG_SET` and `REG_CLR` describe the set/clear alias registers used throughout reset, IRQ, and enable paths.

## Risks And Test Signals
The risk surface is direct hardware programming accuracy. V3 and V4 offsets differ, so callers must use `mxsfb_devdata` for variant-dependent addresses. Width/mask macros assume callers pass values in range. Test signals include compile coverage, register dumps for known modes, IRQ clear/enable behavior, overlay enable/disable validation, and scanout stability under underflow-prone modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/Kbuild

## Purpose
This Kbuild file defines how the Nouveau DRM driver is compiled. It assembles include paths and object lists for NVIF, NVKM, DRM integration, memory management, modesetting, and command submission.

## Important APIs, Types, And Data
It adds include directories for Nouveau public/internal headers and NVKM/GSP subtrees. It includes `nvif/Kbuild` and `nvkm/Kbuild`, then appends many objects to `nouveau-y`. Conditional objects depend on ACPI, debugfs, compat, LEDs, platform driver, SVM, and backlight configuration. It includes `dispnv04/Kbuild` and `dispnv50/Kbuild` for modesetting implementations and finally maps `obj-$(CONFIG_DRM_NOUVEAU)` to `nouveau.o`.

## Control Flow, State, And Integration
There is no runtime control flow. Build flow is modular: lower-level NVIF/NVKM object variables are included first, then the DRM-facing object list is extended. This file integrates the `dispnv04` files in this work item into the complete Nouveau module.

## Risks And Test Signals
Ordering and conditional symbol mismatches can produce missing symbols or dead code. Include path changes can affect both kernel and Nouveau-internal generated headers. Test signals are allmodconfig/allyesconfig builds, builds with optional features toggled, modpost with no unresolved symbols, and ensuring `dispnv04` objects are included when Nouveau is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/Kconfig

## Purpose
This Kconfig file declares Nouveau driver configuration, platform support, debug controls, backlight support, SVM support, and external encoder helper drivers.

## Important APIs, Types, And Data
`CONFIG_DRM_NOUVEAU` is a tristate depending on DRM and PCI, selecting firmware loading, DRM helpers, TTM, GPUVM/scheduler components, I2C, ACPI-related laptop support, power supply, and Tegra devfreq support. `NOUVEAU_PLATFORM_DRIVER` adds Tegra SoC GPU support. Debug level configs control compiled and default log verbosity plus MMU/push-buffer debug. `DRM_NOUVEAU_BACKLIGHT` enables backlight support. `DRM_NOUVEAU_SVM` enables experimental shared virtual memory with HMM/MMU notifier. `DRM_NOUVEAU_CH7006` and `DRM_NOUVEAU_SIL164` expose external encoder modules useful with Nouveau.

## Control Flow, State, And Integration
The file governs dependency closure and optional code inclusion for Nouveau. The external encoder options integrate with legacy display code such as `dfp.c`, which can initialize I2C TMDS encoders like sil164.

## Risks And Test Signals
The wide dependency set means missing selects can surface as build failures only in specific feature combinations. SVM is explicitly experimental and gated by staging/device-private memory support. Test signals include config visibility, build matrix coverage across PCI-only, Tegra, ACPI, backlight, SVM, and encoder-module combinations, and runtime module loading with firmware availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/Kbuild

## Purpose
This Kbuild fragment adds legacy NV04-era Nouveau display implementation objects to the main `nouveau-y` object list.

## Important APIs, Types, And Data
It includes objects for arbitration, CRTC, cursor, DAC, DFP, display setup, low-level hardware helpers, I2C encoders, overlay, TV modes, and NV04/NV17 TV output handling. It also includes the `dispnv04/i2c/Kbuild` subfragment.

## Control Flow, State, And Integration
The fragment is included by the top-level Nouveau Kbuild during module assembly. The files in this work item (`arb.o`, `crtc.o`, `cursor.o`, `dac.o`, `dfp.o`) become part of the legacy display path used by pre-NV50 hardware.

## Risks And Test Signals
Removing or misordering objects can break legacy modesetting symbols. The fragment assumes the top-level include paths have already been set. Test signals are Nouveau builds on configs covering legacy display code, no unresolved `nv04_*`/`nouveau_calc_arb` symbols, and runtime display init on NV04-NV4x GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/arb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/arb.c

## Purpose
`arb.c` calculates legacy NVIDIA display FIFO arbitration parameters. These “magic” burst and low-watermark values prevent display snow or underrun when framebuffer memory is accessed during scanout.

## Important APIs, Types, And Functions
Internal data structures are `struct nv_fifo_info` (`lwm`, `burst`) and `struct nv_sim_state` with pixel/memory/core clocks, bpp, memory type/width/latency/page miss, and two-head state. `nv04_calc_arb()` handles TNT/NV04-style hardware. `nv10_calc_arb()` handles NV10/NV1x-style FIFO sizing and latency. `nv04_update_arb()` gathers clocks and memory parameters from hardware registers and PCI nForce config. `nv20_update_arb()` supplies fixed parameters for later Kelvin-class hardware. Public `nouveau_calc_arb()` chooses the path based on GPU family and chipset.

## Control Flow, State, And Integration
CRTC code calls `nouveau_calc_arb()` during scanout base programming. The function reads current memory/core clocks and memory configuration, computes burst/lwm, and returns encoded values that `crtc.c` writes to VGA extended CRTC registers. No persistent state is stored; outputs are recomputed from current clocks, bpp, and mode pixel clock.

## Risks And Test Signals
The formulas are empirical and hardware-specific. Division by small clock values, bad memory-width detection, dual-head accounting, and chipset exceptions can all produce underruns. The C51/C512 special case returns values in a different-looking scale than the encoded `ilog2` path and must match hardware expectations. Test signals are visual scanout stability under memory pressure, no snow/tearing on NV04-NV2x, dual-head tests, mode switches across bpp/pixel clocks, and register traces matching historical known-good values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/arb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/crtc.c

## Purpose
`crtc.c` implements the legacy NV04 display CRTC path for Nouveau. It is non-atomic KMS code that programs VGA/extended CRTC/RAMDAC state, manages scanout buffer pinning, gamma, hardware cursor upload/positioning, vblank, and push-buffer-driven page flips.

## Important APIs, Types, And Functions
Key mode functions are `nv_crtc_mode_set_vga`, `nv_crtc_mode_set_regs`, `nv_crtc_calc_state_ext`, `nv_crtc_mode_set`, `nv_crtc_prepare`, `nv_crtc_commit`, and `nv04_crtc_mode_set_base`. State save/restore uses `nv_crtc_save` and `nv_crtc_restore`. Display controls include `nv_crtc_dpms`, digital vibrance, image sharpening, gamma load/set, and vblank handler setup. Cursor upload is split between `nv04_cursor_upload` for 16-bit cursor conversion and `nv11_cursor_upload` for ARGB cursor handling. Page flip machinery uses `struct nv04_page_flip_state`, `nv04_page_flip_emit`, `nv04_finish_page_flip`, `nv04_flip_complete`, and `nv04_crtc_page_flip`. `nv04_crtc_create()` allocates the primary plane, CRTC, cursor BO, NVIF head, and vblank event.

## Control Flow, State, And Integration
Mode setting pins the new framebuffer BO, unlocks VGA shadow registers, computes VGA timings, prepares extended mode registers, calculates PLL state, then commit loads the complete mode state and sets base address. Base updates refresh framebuffer format, pitch, start address, gamma if depth changed, and arbitration registers from `nouveau_calc_arb()`. Page flips pin the new BO, synchronize fences, queue flip state under `event_lock`, optionally program swap interval push commands, update display image ownership, emit a software page-flip method, and complete on the NVIF event by setting the CRTC base and arming/sending vblank events.

## State, Dependencies, Risks, And Tests
State spans `nv04_display()->mode_reg/saved_reg/image[]`, `nouveau_crtc` cursor/lut/fb fields, pinned VRAM BO references, VGA CRTC arrays, RAMDAC registers, NVIF head/vblank events, and channel fence flip lists. Dependencies include TTM/GEM BO pinning, Nouveau push/fence/channel code, BIOS PLL parsing, low-level `hw.h`, and `arb.c`. Risks include non-atomic legacy paths, manual refcount/pin lifetime, endian cursor quirks, event/vblank ownership on flip failures, PLL/chipset conditionals, and many undocumented register cargo-cult values. Test signals are legacy modeset, panning, gamma, cursor, DPMS, vblank timestamp, page-flip event, suspend/restore, and multi-head tests on NV04-NV4x cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/cursor.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/cursor.c

## Purpose
`cursor.c` provides the NV04 hardware cursor operation callbacks used by `crtc.c`.

## Important APIs, Types, And Functions
`nv04_cursor_show()` and `nv04_cursor_hide()` call `nv_show_cursor()` for a CRTC head. `nv04_cursor_set_pos()` stores the last x/y and writes `NV_PRAMDAC_CU_START_POS`. `nv04_cursor_set_offset()` encodes the cursor BO offset into extended CRTC cursor-address registers, sets double-scan cursor mode when needed, and applies the NV40 cursor fix on Curie hardware. `nv04_cursor_init()` installs these callbacks into `nouveau_crtc->cursor`.

## Control Flow, State, And Integration
`nv04_crtc_create()` allocates/maps the cursor BO and calls `nv04_cursor_init()`. Later `nv04_crtc_cursor_set()` uploads cursor pixels and calls `set_offset()` and `show()`, while `nv04_crtc_cursor_move()` calls `set_pos()`. State is the saved cursor position, cursor offset, mode register CRTC cursor fields, and live RAMDAC/VGA cursor registers.

## Risks And Test Signals
The cursor address is split across three CRTC registers with chipset-specific workarounds, so offset encoding mistakes cause invisible or corrupt cursors. Double-scan mode and NV40 behavior are explicit risk points. Test signals are cursor visibility, movement, hide/show, correct cursor after modeset, double-scan modes, and NV40 hardware cursor validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/cursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/dac.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/dac.c

## Purpose
`dac.c` implements analog DAC encoder support for legacy Nouveau display hardware, including output offset calculation, load detection, DPMS clock gating, mode setup, save/restore, and encoder creation.

## Important APIs, Types, And Functions
`nv04_dac_output_offset()` maps DCB output routing bits to RAMDAC register offsets. `nv04_dac_detect()` performs NV04-style VGA load detection by manipulating VGA sequencer/CRTC/RAMDAC palette state and sampling during hblank. `nv17_dac_sample_load()` performs newer sample-load detection with PBUS power controls, GPIO TVDAC state, testpoint data, and RAMDAC sense bits; `nv17_dac_detect()` interprets it. Mode helpers include `nv04_dac_mode_fixup`, `nv04_dac_prepare`, `nv04_dac_mode_set`, `nv04_dac_commit`, `nv04_dac_dpms`, save/restore/destroy, `nv04_dac_update_dacclk()`, `nv04_dac_in_use()`, and `nv04_dac_create()`.

## Control Flow, State, And Integration
Encoder creation allocates `nouveau_encoder`, selects NV04 or NV17 helper funcs based on display architecture, initializes a DRM DAC encoder, sets possible CRTCs from DCB heads, and attaches it to the connector. Prepare powers the encoder down and disables any DFP remnants on the target head. Mode set binds DAC clocks to the selected CRTC and programs RAMDAC test control. DPMS tracks `last_dpms` and updates a per-output `dac_users` bitmask so shared DAC clocks are only disabled when no encoder uses them.

## State, Dependencies, Risks, And Tests
State includes DCB output routing, `dac_users`, saved RAMDAC output registers, VGA palette/CRTC/SEQ state during detection, PBUS power-control state, and optional GPIO TVDAC state. Dependencies include low-level Nouveau register helpers, NVIF MMIO access, GPIO subdev, and DCB connector metadata. Risks include flicker during load detection, incomplete head-A-only NV04 detection, fragile save/restore around palette and power controls, shared-DAC conflicts, and chipset-specific test values. Test signals are VGA hotplug/load detection, analog modeset, DPMS cycling, dual-head DAC sharing, TV DAC detection, and restore after suspend/VT switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/dac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/dfp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/dfp.c

## Purpose
`dfp.c` implements digital flat-panel encoder support for legacy Nouveau hardware, covering TMDS and LVDS outputs, flat-panel timing generator control, head binding, scaling, dithering, LVDS power scripts, external TMDS transmitters, and encoder creation.

## Important APIs, Types, And Functions
Important helpers are `nv04_dfp_get_bound_head`, `nv04_dfp_bind_head`, `nv04_dfp_disable`, `nv04_dfp_update_fp_control`, `get_tmds_slave`, `nv04_dfp_mode_fixup`, `nv04_dfp_prepare_sel_clk`, `nv04_dfp_prepare`, `nv04_dfp_mode_set`, `nv04_dfp_commit`, `nv04_lvds_dpms`, `nv04_tmds_dpms`, save/restore/destroy, `nv04_tmds_slave_init`, and `nv04_dfp_create`. It defines `FP_TG_CONTROL_ON/OFF` masks and `is_fpc_off()`.

## Control Flow, State, And Integration
Mode fixup chooses native panel timing when scaling is enabled and the requested mode fits inside the native mode. Prepare powers the encoder down, updates `SEL_CLK`, and routes the digital output to the intended CRTC/head. Mode set fills flat-panel horizontal/vertical register arrays, computes FP control flags for sync polarity, scaling mode, interface width, dual-link, and panel timing; it computes aspect scaling using fixed-point arithmetic and programs dither state based on connector properties and framebuffer depth. Commit runs TMDS or LVDS BIOS scripts, refreshes FP control state, programs DAC test control, initializes external I2C transmitters if needed, then DPMSes on. LVDS DPMS may run panel on/off scripts and update platform-specific backlight bits.

## State, Dependencies, Risks, And Tests
State includes `mode_reg` flat-panel registers, saved FP control/dither/SEL_CLK, CRTC `fp_users`, encoder `last_dpms`, DCB output metadata, connector native mode/scaling/dithering, and external I2C encoder state. Dependencies include BIOS TMDS/LVDS scripts, DCB tables, NVKM I2C, optional sil164 helper, low-level RAMDAC/VGA helpers, and connector properties. Risks include many undocumented chipset-specific bits, dual-link detection from EDID or BIOS tables, external transmitter ambiguity on shared I2C addresses, scaling math edge cases, and LVDS power sequencing. Test signals are LVDS/TMDS modesets, native/center/aspect/full scaling, dithering properties, dual-link high-clock panels, DPMS/backlight behavior, external sil164 output, and suspend/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/dfp.c -->

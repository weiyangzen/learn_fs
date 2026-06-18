# subset-b-001399 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.c

Purpose: Implements the DCN 3.0 VPG generic packet programming path. The VPG object is a hardware block used to write generic secondary data packets into double-buffered GSP memory and trigger either immediate or next-frame updates.

Important APIs/types/functions: `vpg3_update_generic_info_packet()` is the only behavior exposed through `struct vpg_funcs`; `vpg3_construct()` wires a `struct dcn30_vpg` to context, instance id, register table, shifts, masks, and the function table. The implementation depends on `struct dc_info_packet` headers `hb0..hb3` and payload `sb[]`, `REG_WAIT`, `REG_UPDATE`, `REG_SET_4`, and `REG_WRITE`.

Control flow: packet programming validates `packet_index <= 14`, waits for `VPG_GENERIC_CONFLICT_OCCURED` to clear, clears the conflict flag, sets `VPG_GENERIC_DATA_INDEX` to `packet_index * 9`, writes one header dword and eight payload dwords, then sets one of the per-slot update bits. Immediate updates go through `VPG_GSP_IMMEDIATE_UPDATE_CTRL`; deferred updates go through `VPG_GSP_FRAME_UPDATE_CTRL`.

State/persistence: The object persists only pointers to register metadata and base context. Runtime state is hardware register state: generic packet memory, conflict status, and update latches. The function does not retain a software copy of packets.

Dependencies/integration: Used by DCN3 VPG users through the `vpg` abstraction. It integrates with DC register helpers and the display core's info-packet generation path.

Risks: Invalid indexes assert but then fall through to default no-op update behavior; release builds may still program data index for out-of-range values. The payload is cast to `uint32_t *`, so callers must provide the expected packet layout and alignment. Poll timeout is a fixed local value with no error propagation.

Test signals: Exercise all valid packet slots, immediate and frame update modes, conflict-clear behavior, and header/payload dword ordering. Register-trace tests should verify data index increments by nine per packet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.h

Purpose: Declares the DCN 3.0 VPG hardware wrapper, register lists, field shift/mask layouts, and constructor/API prototypes used by display resource construction.

Important APIs/types/functions: `DCN30_VPG_FROM_VPG()` converts the base `struct vpg` to `struct dcn30_vpg`. `VPG_DCN3_REG_LIST()` names the five VPG registers. `DCN3_VPG_MASK_SH_LIST()` and `VPG_DCN3_REG_FIELD_LIST()` enumerate conflict, data, frame-update, and immediate-update fields for 15 generic packet slots. `struct dcn30_vpg_registers`, `struct dcn30_vpg_shift`, `struct dcn30_vpg_mask`, and `struct dcn30_vpg` define the object contract.

Control flow: This header has no runtime control flow; it enables generated/static resource tables to create register, shift, and mask instances consumed by `dcn30_vpg.c`.

State/persistence: `struct dcn30_vpg` stores the embedded base object plus immutable pointers to register/field metadata. Hardware state is external.

Dependencies/integration: Includes `vpg.h` and depends on register-list macros such as `SRI` and `SE_SF` supplied by AMD DC resource files. Its prototypes are implemented by `dcn30_vpg.c` and are reused by DCN31 VPG code for packet writes.

Risks: Macro lists must stay synchronized with silicon register definitions and the switch statements in `vpg3_update_generic_info_packet()`. Omitting a field breaks register helper expansion at compile time or silently prevents a packet slot from updating.

Test signals: Build coverage with DCN3 resources is the primary signal. Register-table smoke tests should confirm all 15 frame and immediate update fields resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/Makefile

Purpose: Adds the DCN301 display core object list to the AMD display build.

Important APIs/types/functions: Defines `DCN301 = dcn301_panel_cntl.o`, prefixes it with `$(AMDDALPATH)/dc/dcn301/` into `AMD_DAL_DCN301`, and appends it to `AMD_DISPLAY_FILES`.

Control flow: Makefile expansion only; no runtime flow.

State/persistence: It persists one build-time object selection. The resulting object is linked into the display driver when this directory's make fragment is included.

Dependencies/integration: Integrated by the parent AMD DC make system through `AMD_DISPLAY_FILES`. It assumes `dcn301_panel_cntl.c` is the only DCN301-specific core object in this subset.

Risks: The comment says "Makefile for dcn30" although the path and variables are DCN301; this is cosmetic but can confuse maintenance. Missing objects here would compile out DCN301-specific behavior even when sources exist.

Test signals: Kernel/display-driver build should include `dc/dcn301/dcn301_panel_cntl.o` in `AMD_DISPLAY_FILES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.c

Purpose: Implements DCN301 panel power/backlight control using direct PWM and power-sequencer registers.

Important APIs/types/functions: `dcn301_panel_cntl_construct()` initializes the panel controller function table. Static handlers implement `hw_init`, destroy, backlight-on query, power-on query, backlight register store, and current-backlight calculation. `dcn301_get_16_bit_backlight_from_pwm()` converts PWM period/count/fractional state into a 16-bit backlight value.

Control flow: Hardware init reads `BL_ACTIVE_INT_FRAC_CNT`. If BIOS left invalid values `0` or `1`, it restores cached PWM registers or writes fallback defaults. Otherwise it caches current PWM registers and reference divider. It enables PWM output, unlocks group 1 registers, computes the current backlight, and returns it. State queries read `PANEL_BLON`, `PANEL_PWRSEQ_TARGET_STATE_R`, `PANEL_DIGON`, and `PANEL_DIGON_OVRD`.

State/persistence: Persistent software state lives in `panel_cntl->stored_backlight_registers`. Hardware state is PWM control, period, reference divider, group lock, and power-sequencer bits.

Dependencies/integration: Depends on `panel_cntl`, `dce_panel_cntl` register definitions, DC register helpers, and kernel `kfree`. It provides `struct panel_cntl_funcs` to higher display code.

Risks: Backlight math uses bit shifts based on `BL_PWM_PERIOD_BITCNT`; invalid or unexpected bit counts could overflow masks. Fallback constants are hardware-specific. Register writes occur without an explicit DMUB mediation layer, unlike DCN31.

Test signals: Validate BIOS-bug recovery, cache/store/restore behavior, PWM-to-16-bit conversion with fractional and non-fractional modes, and power/backlight query bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.h

Purpose: Declares the DCN301 direct-register panel controller type and its register/field metadata.

Important APIs/types/functions: `DCN301_PANEL_CNTL_REG_LIST()` maps power sequencer and PWM registers. `DCN301_PANEL_CNTL_MASK_SH_LIST()` and `DCN301_PANEL_CNTL_REG_FIELD_LIST()` enumerate panel power, PWM duty, fractional enable, register lock, update pending, and reference divider fields. `struct dcn301_panel_cntl` embeds `struct panel_cntl` and stores register, shift, and mask tables.

Control flow: Header-only declarations; construction and function dispatch are implemented in the C file.

State/persistence: The structure keeps metadata pointers; mutable backlight cache is inherited from `struct panel_cntl`.

Dependencies/integration: Includes `panel_cntl.h` and `dce/dce_panel_cntl.h`, tying DCN301 to the generic panel controller abstraction and DCE-era register naming.

Risks: Field-list order must match generated shift/mask initializers. The register list assumes `id`-indexed panel/PWM instances; wrong resource wiring would direct backlight writes to the wrong hardware block.

Test signals: Compile-time expansion in DCN301 resource code and direct-register backlight tests that use every field declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/Makefile

Purpose: Adds DCN31-specific display core objects to the AMD display build.

Important APIs/types/functions: Defines `DCN31 = dcn31_panel_cntl.o dcn31_apg.o dcn31_afmt.o dcn31_vpg.o`, prefixes with `$(AMDDALPATH)/dc/dcn31/`, and appends to `AMD_DISPLAY_FILES`.

Control flow: Build-time list expansion only.

State/persistence: Persists the object set included for DCN31 display support.

Dependencies/integration: Included by the larger AMD DC make hierarchy. The object list provides panel control, APG audio packet generation, AFMT audio formatting, and VPG packet generation support.

Risks: Missing or stale object names cause link-time failures or absent hardware hooks. The list must stay aligned with resource constructors that reference these modules.

Test signals: A configured AMD display build should compile and link all four DCN31 objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.c

Purpose: Implements DCN31 AFMT object construction and memory low-power control while reusing DCN30 AFMT audio setup functions.

Important APIs/types/functions: `afmt31_construct()` binds a `struct dcn31_afmt` to context, instance, register tables, and `dcn31_afmt_funcs`. `afmt31_powerdown()` and `afmt31_poweron()` program `AFMT_MEM_PWR`. The function table delegates HDMI/DP audio setup, mute, and audio info updates to `afmt3_*` routines.

Control flow: Powerdown returns immediately unless `debug.enable_mem_low_power.bits.afmt` is set, then clears `AFMT_MEM_PWR_DIS` and forces memory low power. Poweron also honors the debug flag and writes the inverse force/disable values.

State/persistence: Software state is just object metadata. Hardware state is AFMT memory power force/disable bits plus the inherited AFMT audio registers programmed by delegated functions.

Dependencies/integration: Includes DCN30 AFMT helpers, `dc/dc.h` debug flags, and register helpers. Stream encoder HDMI/DP audio paths can call AFMT power hooks through `enc->afmt`.

Risks: Low-power behavior is gated by a debug bit, so tests must cover both enabled and disabled paths. Incorrect polarity on `AFMT_MEM_PWR_DIS`/`AFMT_MEM_PWR_FORCE` would cause audio formatting memory to remain powered down or never enter low power.

Test signals: Register tests should confirm no writes when AFMT low power is disabled, and correct `AFMT_MEM_PWR` writes during HDMI audio disable or display idle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h

Purpose: Declares the DCN31 AFMT hardware wrapper, register list, field metadata, power hooks, and constructor.

Important APIs/types/functions: `DCN31_AFMT_FROM_AFMT()` casts the base `struct afmt`. `AFMT_DCN31_REG_LIST()` adds AFMT audio/infoframe/channel-status registers and `AFMT_MEM_PWR`. `DCN31_AFMT_MASK_SH_LIST()` and `AFMT_DCN31_REG_FIELD_LIST()` cover audio source, channel enable, IEC 60958 channel status, sample send, and memory power fields. `struct dcn31_afmt` embeds `struct afmt`.

Control flow: Header-only declarations; dispatch is through `struct afmt_funcs` set in the C file.

State/persistence: Stores immutable register/shift/mask pointers and base context/instance.

Dependencies/integration: Consumed by DCN31 resource construction and by stream/audio encoder paths that need AFMT power control.

Risks: Register-field macro coverage must include all fields used by delegated DCN30 AFMT helpers, not just fields touched in `dcn31_afmt.c`. Missing `AFMT_MEM_PWR_STATE` support can limit diagnostics.

Test signals: Build with DCN31 resources and AFMT audio smoke tests for HDMI/DP channel status and memory low-power fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.c

Purpose: Implements the DCN31 APG audio packet generator abstraction for DP audio setup, reset, enable, and disable.

Important APIs/types/functions: `apg31_construct()` initializes the object and `dcn31_apg_funcs`. `apg31_enable()` resets APG and enables it. `apg31_disable()` clears `APG_ENABLE`. `apg31_se_audio_setup()` configures stream id, channel enable, and memory power force.

Control flow: Enable asserts `APG_RESET`, waits for `APG_RESET_DONE`, deasserts reset, waits for reset done to clear, then sets `APG_ENABLE`. Audio setup ignores `az_inst`, asserts non-null `audio_info`, sets DP audio stream id to `0`, enables all debug audio channels with `0xFF`, and clears forced APG memory power off.

State/persistence: Software state is base context/instance and register metadata. Hardware state is APG reset, enable, stream id, debug channel mask, and APG memory power force.

Dependencies/integration: Provides `struct apg_funcs` used by DCN31 audio/display code. Depends on register helpers and `struct audio_info` from the display stack.

Risks: `setup_hdmi_audio` exists in the function type but is not implemented in the function table. `audio_info` content is not actually used after the null check, so speaker/channel-specific policy is elsewhere. Reset waits have fixed retry counts.

Test signals: Confirm reset sequencing, enable/disable bit writes, null `audio_info` handling, DP stream id `0`, and all-channel debug mask programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h

Purpose: Declares the DCN31 APG base abstraction and concrete register-backed implementation.

Important APIs/types/functions: `DCN31_APG_FROM_APG()` casts from `struct apg`. `APG_DCN31_REG_LIST()` lists APG control, control2, memory power, and debug generation registers. Field macros cover reset, reset done, enable, DP audio stream id, debug channel enable, and memory power force. `struct apg_funcs` exposes setup, enable, and disable callbacks.

Control flow: No runtime flow in the header; consumers call the function table populated by `apg31_construct()`.

State/persistence: `struct apg` stores function table, context, and instance. `struct dcn31_apg` adds register/shift/mask table pointers.

Dependencies/integration: Used by DCN31 resource creation and audio path code. The header declares its own base `struct apg`, making it the local interface owner for APG users.

Risks: The include guard says `AGP` instead of `APG`, a spelling issue but functionally harmless if unique. The `setup_hdmi_audio` callback signature has no parameters beyond `struct apg *`, so HDMI support would require care if added.

Test signals: Compile coverage plus APG register programming tests for reset, enable, stream id, and memory-power fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_panel_cntl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_panel_cntl.c

Purpose: Implements DCN31 panel control through DMUB commands rather than direct PWM register programming.

Important APIs/types/functions: `dcn31_panel_cntl_construct()` installs `panel_cntl_funcs` and maps the panel to a power sequencer instance. `dcn31_query_backlight_info()` sends `DMUB_CMD__PANEL_CNTL_QUERY_BACKLIGHT_INFO`. `dcn31_panel_cntl_hw_init()` sends `DMUB_CMD__PANEL_CNTL_HW_INIT` and optionally `DMUB_CMD__PANEL_DEBUG_PWM_FREQ`.

Control flow: Query helpers zero a `union dmub_rb_cmd`, fill header type/subtype/payload size and `pwrseq_inst`, then call `dc_wake_and_execute_dmub_cmd(...WAIT_WITH_REPLY)`. Hardware init passes cached PWM/ref-divider values to DMUB, stores returned values back into `stored_backlight_registers`, optionally sends debug PWM frequency if within `200..6250 Hz`, then returns current backlight. Constructor maps power sequencer by DIG engine when `support_edp0_on_dp1` is set; otherwise it uses the panel instance.

State/persistence: Persistent state is the base panel controller, `pwrseq_inst`, and cached backlight registers returned by DMUB. Hardware details are owned by DMUB firmware.

Dependencies/integration: Depends on `dc_dmub_srv`, DMUB command formats, panel controller abstraction, and DC config/debug fields.

Risks: If `dmub_srv` is absent or a command fails, APIs return `0` or `false`, which is indistinguishable from valid off/zero backlight to some callers. Unsupported engine ids assert and log but leave `pwrseq_inst` as `0xF`.

Test signals: Mock DMUB replies for init/query paths, test debug frequency bounds, verify pwrseq mapping for DIGA/DIGB and legacy mode, and failure handling when DMUB is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_panel_cntl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_panel_cntl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_panel_cntl.h

Purpose: Declares the DCN31 DMUB-backed panel controller.

Important APIs/types/functions: Defines debug PWM frequency bounds `MIN_DEBUG_FREQ_HZ` and `MAX_DEBUG_FREQ_HZ`, `struct dcn31_panel_cntl` embedding `struct panel_cntl`, and `dcn31_panel_cntl_construct()`.

Control flow: None in the header; all behavior is through the function table set by the constructor.

State/persistence: No DCN31-specific fields beyond the inherited base; `pwrseq_inst` and cached backlight registers live in `struct panel_cntl`.

Dependencies/integration: Includes `panel_cntl.h` and `dce/dce_panel_cntl.h` so it can reuse common panel storage while delegating hardware operations to DMUB in the C file.

Risks: Because this structure has no register table, any caller expecting DCN301-style direct register access would be incompatible. Frequency bounds must stay aligned with firmware expectations.

Test signals: Build-time constructor references and runtime tests for DMUB command population using inherited panel fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_panel_cntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.c

Purpose: Implements DCN31 VPG construction and memory low-power hooks while reusing the DCN30 generic packet writer.

Important APIs/types/functions: `vpg31_construct()` initializes `struct dcn31_vpg`. `vpg31_powerdown()` and `vpg31_poweron()` program `VPG_MEM_PWR`. The function table exposes `.update_generic_info_packet = vpg3_update_generic_info_packet`, `.vpg_poweron`, and `.vpg_powerdown`.

Control flow: Powerdown returns unless `debug.enable_mem_low_power.bits.vpg` is enabled, then clears light-sleep disable and forces light sleep. Poweron reads `VPG_GSP_MEM_PWR_STATE`; if VPG low power is disabled and state is already `0`, it returns, otherwise it disables light sleep and clears force.

State/persistence: Software state is context, instance, function table, and register metadata. Hardware state is inherited generic packet memory/update state plus VPG memory power bits.

Dependencies/integration: Includes `dcn30_vpg.h` for packet programming and `dc/dc.h` for debug low-power flags. Used by DCN31 resource creation.

Risks: The poweron condition has a subtle debug/state dependency; incorrect `VPG_GSP_MEM_PWR_STATE` interpretation could skip wake-up. Packet behavior inherits DCN30's fixed retry and out-of-range-index characteristics.

Test signals: Test low-power disabled/enabled paths, power-state read behavior, and that DCN31 still writes generic packets through `vpg3_update_generic_info_packet()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h

Purpose: Declares the DCN31 VPG wrapper, extending DCN30-style generic packet registers with memory power control.

Important APIs/types/functions: `VPG_DCN31_REG_LIST()` lists generic packet/status/update registers plus `VPG_MEM_PWR`. Field macros include the 15 generic packet frame/immediate update bits and `VPG_GSP_MEM_LIGHT_SLEEP_DIS`, `VPG_GSP_LIGHT_SLEEP_FORCE`, and `VPG_GSP_MEM_PWR_STATE`. `struct dcn31_vpg` mirrors DCN30 with DCN31 register metadata.

Control flow: Header declarations only.

State/persistence: Stores immutable register/shift/mask pointers and the inherited `struct vpg` base.

Dependencies/integration: Includes `vpg.h`; implemented by `dcn31_vpg.c` and integrated with DCN31 resource construction.

Risks: Duplicates much of DCN30 VPG metadata, so changes to generic packet slots must be mirrored. Missing memory-power fields would compile but disable low-power hooks.

Test signals: Compile-time resource expansion and register traces for packet slots plus VPG memory power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/Makefile

Purpose: Aggregates AMD DC Display I/O objects for virtual encoders and multiple DCN hardware generations.

Important APIs/types/functions: Always adds `virtual_link_encoder.o` and `virtual_stream_encoder.o`. Under `CONFIG_DRM_AMD_DC_FP`, it adds DCN10, DCN20, DCN30, DCN301, DCN31, DCN314, DCN32, DCN35, DCN321, DCN401, and DCN42 DIO object lists to `AMD_DISPLAY_FILES`.

Control flow: Build-time conditional expansion based on `CONFIG_DRM_AMD_DC_FP`.

State/persistence: Persists the set of DIO objects linked into the driver for a configuration.

Dependencies/integration: Relies on `AMDDALPATH` and the parent AMD display make system. The floating-point config gate controls physical DCN DIO implementations while virtual encoders remain available.

Risks: A missing object here silently removes a generation-specific encoder implementation from builds. The broad `CONFIG_DRM_AMD_DC_FP` gate means non-FP builds do not get the physical DCN DIO modules.

Test signals: Build logs/object lists should show virtual objects unconditionally and generation-specific objects only with `CONFIG_DRM_AMD_DC_FP=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_dio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_dio.c

Purpose: Implements the small DCN10 DIO block-level memory power control object.

Important APIs/types/functions: `dcn10_dio_construct()` initializes a `struct dcn10_dio` with context, function table, and register metadata. `dcn10_dio_mem_pwr_ctrl()` writes `DIO_MEM_PWR_CTRL` and optionally forces I2C light sleep.

Control flow: Memory power control first writes `0` to `DIO_MEM_PWR_CTRL`, described as powering AFMT HDMI memory, then sets `I2C_LIGHT_SLEEP_FORCE` when requested. Constructor only stores pointers and function table.

State/persistence: Software state is register metadata and context. Hardware state is the DIO memory power control register and I2C light-sleep bit.

Dependencies/integration: Implements `struct dio_funcs` from `dio.h`; uses DC register helper macros.

Risks: The function name takes `enable_i2c_light_sleep` but always clears the whole register first, so callers must account for collateral bit resets. There is no read-modify preservation of unrelated fields.

Test signals: Register write traces for both `enable_i2c_light_sleep=false` and `true`, plus constructor/function-table smoke coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_dio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_dio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_dio.h

Purpose: Declares the DCN10 DIO memory power control wrapper.

Important APIs/types/functions: `TO_DCN10_DIO()` casts from `struct dio`. `DIO_REG_LIST_DCN10()` lists `DIO_MEM_PWR_CTRL`. `struct dcn_dio_registers`, `struct dcn_dio_shift`, and `struct dcn_dio_mask` expose the `I2C_LIGHT_SLEEP_FORCE` field. `struct dcn10_dio` embeds `struct dio`.

Control flow: Header-only; behavior is provided by `dcn10_dio.c`.

State/persistence: Stores base object and immutable register metadata pointers.

Dependencies/integration: Includes `dio.h` and is consumed by DCN resource construction.

Risks: Only one field is modeled, so any future use of other `DIO_MEM_PWR_CTRL` fields requires extending the mask/shift structs before using register helpers.

Test signals: Compile coverage and register metadata initialization for `DIO_MEM_PWR_CTRL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_dio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.c

Purpose: Implements the DCN10 link encoder: the DIG backend/PHY control surface for DVI, HDMI, DP SST, DP MST, eDP, HPD, AUX, PSR, DP training, and MST allocation.

Important APIs/types/functions: The `dcn10_lnk_enc_funcs` table exposes validation, init, setup, TMDS/DP/MST enable, output disable, lane settings, PHY pattern programming, MST SAT updates, PSR helpers, DIG FE/BE connection, HPD/AUX, capability queries, and destroy. Construction reads VBIOS encoder capability info and maps transmitters to preferred DIG engines.

Control flow: Validation dispatches by stream signal and checks DVI/HDMI/DP limits, color depth, pixel encoding, EDID max TMDS clock, HDMI 2.0 debug disable, and YCbCr420 support. Hardware init calls VBIOS transmitter init, handles LVDS brightness, initializes AUX, and associates HPD. Output enable routes through VBIOS transmitter-control tables after programming lanes/modes. DP PHY pattern paths set training patterns, PRBS, D102, 80-bit custom, CP2520 compliance, or video passthrough. MST allocation writes up to four stream rows, triggers SAT update, and polls completion/keepout.

State/persistence: Persistent object state includes base capabilities, transmitter, connector, HPD GPIO/source, preferred engine, and register metadata. Hardware state includes DIG mode/source, DP lane count, training complete, PHY bypass/PRBS/symbols, MST SAT, HPD enable/filter, and AUX settings.

Dependencies/integration: Depends on DC BIOS transmitter/encoder-control tables, GPIO/IRQ services, stream encoders, link settings, DPCD training fields, and register helpers.

Risks: Many paths rely on VBIOS return status; failures log and break to debugger but often do not propagate to higher layers. Some validation mutates `max_hdmi_pixel_clock` when SCDC overwrite is skipped. Fixed polling for MST update may time out silently. Custom pattern programming assumes a 10-byte pattern.

Test signals: Cover stream validation matrix, VBIOS command parameters for TMDS/DP/MST, DP lane settings per lane, every PHY test pattern, MST allocation rows and timeout path, HPD filter programming, AUX initialization, and DIG mode/source readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.h

Purpose: Declares the DCN10 link encoder register model, common field lists reused by newer DCN generations, and the public link-encoder API implemented in `dcn10_link_encoder.c`.

Important APIs/types/functions: Register structs cover link, AUX, and HPD blocks. Macro field lists span DIG enable/mode/source, DP DPHY, MST SAT, AUX, HPD, and many DCN20+ DPCS/UNIPHY fields used by derived encoders. `struct dcn10_link_encoder` embeds `struct link_encoder` and stores register metadata. Prototypes expose construction, validation, init, setup, enable/disable, lane training, MST allocation, PSR, AUX, HPD, capability, and readback helpers.

Control flow: None in the header; it defines the static interface and macro expansion surface used by resource tables.

State/persistence: The C object stores base link encoder state and immutable register metadata pointers. HPD GPIO lifetime is owned through the base and destroyed by the C implementation.

Dependencies/integration: Includes `link_encoder.h` and is included by DCN20 link encoder headers for inheritance/reuse.

Risks: This header is a shared compatibility point for multiple generations, so adding/removing fields can affect DCN20, DCN30, DCN31, and DCN35 users. Some prototypes such as RGB/wireless validation are declared here but not implemented in the reviewed C file, so users must not assume every declaration is locally defined.

Test signals: Compile/link coverage across all DIO generations using the shared field lists, plus resource-table initialization tests for AUX/HPD/link register mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.c

Purpose: Implements the DCN10 stream encoder: timing/MSA programming, HDMI/DVI setup, DP/HDMI info packets, DP blank/unblank, MST VCP rate, audio packets, stereo sync, AV mute, and DIG-to-OTG routing.

Important APIs/types/functions: `dcn10_stream_encoder_construct()` installs `dcn10_str_enc_funcs`. Major APIs include DP/HDMI/DVI stream attribute setters, generic info packet writer, DP/HDMI packet update/stop helpers, immediate SDP send, DP blank/unblank, audio setup/enable/disable for DP and HDMI, audio clock lookup, and DP pixel format readback.

Control flow: DP attribute setup normalizes interlaced timing, maps pixel encoding/depth/color space into DP registers, and programs MSA timing. HDMI setup calls VBIOS encoder control, configures deep color and scrambling, enables mandatory packets, and clears AV mute. Info packet paths write AFMT generic slots and toggle HDMI or DP secondary-packet enables. DP blank defers disable to vblank, polls stream status, and resets steer FIFO; unblank programs M/N, starts DIG, releases FIFO, delays, and enables stream. Audio setup maps speakers to CEA channels, writes ACR/N/CTS tables or fallback values, and enables DP/HDMI audio packets.

State/persistence: Persistent state is base context, BIOS, engine id, register metadata, and stream encoder instance. Hardware state includes AFMT generic packet memory, DP MSA/timing, HDMI control/infoframe registers, DP secondary-packet enables, audio clock/channel registers, DIG source, and FIFO state.

Dependencies/integration: Depends on DC BIOS encoder control, link service DP trace hooks, fixed-point helpers, DPCD source sequence tracing, and AFMT power hooks.

Risks: Several packet writers cast byte payloads to `uint32_t *` and assume layout/alignment. Fixed waits may hide hardware stalls. DP info packet slot 1 is reserved for PSR firmware, and slot 4 for immediate SDP, so callers must avoid collisions. HDMI audio tables must match spec clocks.

Test signals: DP MSA register programming for RGB/YUV/interlace/colorimetry, HDMI deep-color/scramble behavior, info packet slot enable/disable, DP blank/unblank trace order, MST VCP fixed-point rounding, audio clock table lookup/fallback, speaker channel mapping, and pixel format readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.h

Purpose: Declares the DCN10 stream encoder register model, field macro lists shared by later generations, concrete object type, and public stream encoder helpers.

Important APIs/types/functions: `SE_COMMON_DCN_REG_LIST()` and `struct dcn10_stream_enc_registers` cover AFMT, HDMI, DP MSA, DP secondary-packet, DSC/metadata, DIG FIFO/clock, and audio registers. Field lists span DCN1.0 through DCN4.01 and audio-common extensions. Prototypes cover construction, DP/HDMI/DVI setup, packet updates, blank/unblank, audio, DIG routing, HDMI reset, audio clock lookup, and DP pixel format readback.

Control flow: Header-only; function dispatch occurs through `struct stream_encoder_funcs` in C files.

State/persistence: `struct dcn10_stream_encoder` embeds the base stream encoder and stores register/shift/mask metadata. Runtime hardware state is external to the struct.

Dependencies/integration: Includes `stream_encoder.h`; reused by DCN20 stream encoder and newer modules via common register/field lists.

Risks: This is a cross-generation macro surface; field-list drift can break unrelated generations. Register structs include fields not present on every generation, so resource code must provide correct zero or real addresses.

Test signals: Cross-generation build coverage, resource-table initialization, and function-table users compiling against all declared helper prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.c

Purpose: Extends the DCN10 link encoder for DCN20 with FEC control, DCN2 AUX initialization, USB-C alt-mode awareness, and an optional VBIOS-avoidance DP path.

Important APIs/types/functions: `dcn20_link_encoder_construct()` installs `dcn20_link_enc_funcs`. `enc2_fec_set_enable()`, `enc2_fec_set_ready()`, and `enc2_fec_is_active()` manage FEC bits. `link_enc2_read_state()` captures FEC/training state. `dcn20_link_encoder_enable_dp_output()` optionally uses `dcn10_link_encoder_enable_dp_output()` or updates local `dpcssys_phy_seq_cfg`. `enc2_hw_init()` programs AUX DPHY from a golden table or defaults.

Control flow: FEC APIs are direct register updates/readback. DP enable delegates to DCN10 unless `debug.avoid_vbios_exec_table` is set; in that mode it selects an MPLL config by link rate, marks lanes enabled, configures DIG lanes, and sets DP mode without running VBIOS. Max link capability starts from DCN10 and clamps lane count to two when USB-C alt mode is not four-lane. Hardware init writes AUX DPHY controls, sets legacy `TMDS_CTL0`, and initializes AUX HPD selection.

State/persistence: Adds `phy_seq_cfg` under `struct dcn20_link_encoder`; most persistent base state remains in embedded `dcn10_link_encoder`. Hardware state includes FEC bits, AUX DPHY settings, USB-C alt-mode fields, and inherited DIG/DP/HPD state.

Dependencies/integration: Reuses DCN10 helpers heavily, depends on VBIOS golden table values, DC debug flags, and DCN20 DPCS/UNIPHY register fields.

Risks: The VBIOS-avoidance path is partial: it prepares config and mode but does not perform the full transmitter table sequence. Unsupported link rates log and abort. Alt-mode lane limiting depends on `DP_IS_USB_C` and register state.

Test signals: FEC enable/ready/active readback, AUX golden-table/default writes, USB-C DP2 lane clamp, DP output with and without `avoid_vbios_exec_table`, and state capture for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.h

Purpose: Declares the DCN20 link encoder extension over the DCN10 base, including AUX, UNIPHY, DPCS, FEC, MPLL, and USB-C alt-mode fields.

Important APIs/types/functions: `DCN2_AUX_REG_LIST()`, `UNIPHY_MASK_SH_LIST()`, `DPCS_MASK_SH_LIST()`, `DPCS_DCN2_MASK_SH_LIST()`, and `LINK_ENCODER_MASK_SH_LIST_DCN20()` define DCN2 register coverage. `struct mpll_cfg` models PLL parameters by link rate. `struct dpcssys_phy_seq_cfg` holds lane enables, fuse/SRAM/calibration flags, and selected MPLL config. `struct dcn20_link_encoder` embeds `struct dcn10_link_encoder`.

Control flow: Header declarations only; C code consumes these structures during construction, DP enable, and FEC/AUX operations.

State/persistence: Adds persistent `phy_seq_cfg` to the embedded DCN10 encoder state. Register metadata remains via the inherited `dcn10_link_encoder`.

Dependencies/integration: Includes `dcn10/dcn10_link_encoder.h`, making DCN20 a structural extension rather than an independent implementation.

Risks: Very large field macro lists are error-prone and shared by later generations. The disabled `#if 0` fields in `dpcssys_phy_seq_cfg` document intended PHY sequencing but are not active, so direct PHY programming remains incomplete.

Test signals: Compile-time field coverage, resource register initialization, FEC field access, USB-C alt-mode fields, and MPLL config selection for RBR/HBR/HBR2/HBR3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_stream_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_stream_encoder.c

Purpose: Extends the DCN10 stream encoder for DCN20 features: expanded HDMI generic packet control, DSC PPS/config, dynamic metadata, SDP line selection, ODM combine, adjusted DP unblank sequencing, and FIFO diagnostics.

Important APIs/types/functions: `dcn20_stream_encoder_construct()` installs `dcn20_str_enc_funcs`. DCN20-specific handlers include HDMI packet update/stop, `enc2_dp_set_dsc_config()`, `enc2_dp_set_dsc_pps_info_packet()`, `enc2_set_dynamic_metadata()`, `enc2_stream_encoder_update_dp_info_packets_sdp_line_num()`, `enc2_stream_encoder_dp_unblank()`, `enc2_dp_set_odm_combine()`, and `enc2_get_fifo_cal_average_level()`.

Control flow: HDMI packet programming separates continuous/send bits from line registers and adds VTEM on packet 6. DSC PPS writes a 128-byte PPS SDP into GSP slots 7-10, configures PPS mode, line numbers, VBID6 update line, and enables GSP7. Dynamic metadata selects DP or HDMI/Dolby Vision packet paths, sets HUBP requestor and stream type, then enables or disables DME and packet transmission. DP unblank computes M/N with two-pixel-container and OPP-count handling, forces stream disabled, waits for status, toggles DIG start and steer FIFO reset, delays, then enables video. DP stream attributes reuse DCN10 and add `DP_SST_SDP_SPLITTING`.

State/persistence: Software state is inherited DCN10 stream encoder metadata. Hardware state includes DSC mode/slice/bytes-per-pixel, PPS GSP memory, VBID6 and GSP7 line controls, metadata engine and packet controls, ODM combine, SDP splitting, FIFO state, and inherited HDMI/DP/audio registers.

Dependencies/integration: Reuses many DCN10 helpers and depends on DSC packed PPS data, dynamic metadata modes, link service tracing, and Linux delays.

Risks: PPS writer assumes `hb1` is PPS and writes four generic packet slots from a 128-byte buffer; invalid buffers would corrupt SDP contents. Dynamic metadata changes require OTG master update lock by contract but this function does not enforce it. DP unblank waits up to 5000 iterations and may hide persistent stream-status failures.

Test signals: DSC enable/disable and PPS content/line programming, dynamic metadata for DP/HDMI/Dolby Vision, VTEM HDMI packet slot, adaptive-sync SDP line override, two-pixel-container M/N behavior, FIFO reset sequencing, ODM combine bit, and DSC state readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_stream_encoder.c -->

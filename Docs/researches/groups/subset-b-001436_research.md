# subset-b-001436 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_gpio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_gpio.c

Purpose: Implements the common hardware GPIO pin behavior used by AMD display core GPIO-derived pin classes. It owns open/close state preservation, mode programming, and simple value reads/writes through register helper macros bound to the pin's `gpio_registers`.

Important APIs and functions: `dal_hw_gpio_open` snapshots `MASK`, `A`, and `EN`, programs the requested mode, and sets `hw_gpio_pin.opened`. `dal_hw_gpio_close` restores those saved registers and resets mode/open state. `dal_hw_gpio_get_value` reads `Y` for input/output/hardware/fast-output modes. `dal_hw_gpio_set_value` writes `A` for normal output and toggles `EN` inverted for fast output. `dal_hw_gpio_config_mode` is the central mode switch for input, output, fast output, hardware, and interrupt. `dal_hw_gpio_construct` and `dal_hw_gpio_destruct` initialize and assert lifecycle invariants.

Control flow: callers receive a `hw_gpio_pin` interface from a factory or subclass, call `open(mode)`, then issue value/config/mode operations through function pointers, and finally `close()`. The implementation converts the base pointer with `FROM_HW_GPIO_PIN`, then performs direct register updates. The interrupt mode is deliberately only a GPIO mask setup here; HPD subclasses provide interrupt-specific semantics.

State and persistence: state is volatile hardware register state, with a small in-memory `store` shadow used only between open and close. No persistent storage is used. A risk is that `GPIO_MUX_CONTROL` is not saved/restored despite a TODO, so future mux users could leak mux state across open/close.

Dependencies and integration: depends on `dm_services.h`, `gpio_types.h`, `gpio_regs.h`, and `reg_helper.h`. It is integrated by derived GPIO types such as HPD/DDC/generic pins and by hardware factory code that fills `regs`.

Risks and test signals: test via register trace or mocked `REG_*` helpers for each mode, including restoration on close and inverted fast-output `EN` behavior. Hardware tests should cover DDC fast output rise-time behavior and confirm interrupt-mode callers do not expect value semantics from this base file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_gpio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_gpio.h

Purpose: Declares the common GPIO pin object model for AMD display core. It defines the base `hw_gpio_pin`, the virtual function table, register-address containers, and the concrete `hw_gpio` storage used by common GPIO operations.

Important APIs and types: `struct hw_gpio_pin` is the public base with function pointers, GPIO id, enable index, current mode, opened flag, and DC context. `struct hw_gpio_pin_funcs` defines destroy/open/get/set/config/change/close operations. `struct hw_gpio` embeds the base pin, saved register fields, mux capability flag, and `gpio_registers`. `FROM_HW_GPIO_PIN` and `HW_GPIO_FROM_BASE` are container conversions. Public functions mirror the implementation in `hw_gpio.c`.

Control flow: factory or specialized constructors allocate a larger object, embed `hw_gpio`, assign the function table, and then generic callers interact only through `hw_gpio_pin_funcs`. Register members are populated by derived classes so common code can run the same sequences over different physical GPIO banks.

State and persistence: the header exposes `mode` and `opened` as mutable lifecycle state and `store` as temporary register save space. There is no locking in this API; callers must provide ordering through higher-level GPIO/resource management.

Dependencies and integration: includes `gpio_regs.h` and relies on enums/types from GPIO/DC headers included before it by translation units. It integrates with HPD, DDC, generic GPIO classes, and ASIC-specific hardware factories that bind register tables.

Risks and test signals: ABI risk centers on struct layout and function table compatibility across derived classes. Tests should verify every subclass initializes `funcs`, `regs`, context, and open state before use, and that new mux-aware hardware also extends save/restore behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_hpd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_hpd.c

Purpose: Implements the HPD-specific GPIO subclass for hot-plug-detect pins. It reuses generic GPIO behavior for normal modes and overrides value/config handling needed for interrupt/sense debounce.

Important APIs and functions: `dal_hw_hpd_init` allocates and constructs an HPD pin. `dal_hw_hpd_get_pin` returns the embedded `hw_gpio_pin` from a higher-level `gpio`. `dal_hw_hpd_get_value` reads `DC_HPD_SENSE_DELAYED` when in `GPIO_MODE_INTERRUPT`; otherwise it delegates to `dal_hw_gpio_get_value`. `dal_hw_hpd_set_config` programs connect/disconnect interrupt delays in `toggle_filt_cntl`. The local function table binds common open/set/change/close with HPD-specific get/config/destroy.

Control flow: initialization allocates `struct hw_hpd`, calls the common GPIO constructor, then assigns the HPD vtable. During interrupt-mode reads, the code bypasses the generic GPIO `Y` register and reads HPD interrupt status. Config updates divide millisecond-like delay fields by 10 before writing hardware fields.

State and persistence: lifecycle state lives in the embedded `hw_gpio`. HPD-specific register table pointers are expected to be assigned by ASIC factory code after allocation. There is no persisted state; hardware debounce configuration persists in registers until reprogrammed.

Dependencies and integration: depends on `gpio_interface.h`, `hw_gpio.h`, `hpd_regs.h`, and `reg_helper.h`. It integrates with GPIO factory setup and with display link detection/interrupt handling that obtains HPD pins through `dal_hw_hpd_get_pin`.

Risks and test signals: `dal_hw_hpd_init` sets `*hw_hpd = NULL` for invalid `en` but does not immediately return, so later allocation may overwrite that unless callers never pass invalid values. Tests should cover interrupt-mode sense reads, debounce programming units, invalid/null config handling, allocation failure, and factory population of `regs`, `shifts`, and `masks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_hpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_hpd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_hpd.h

Purpose: Declares the HPD GPIO subclass layout and construction helpers. HPD pins extend `hw_gpio` with HPD interrupt/status register metadata.

Important APIs and types: `struct hw_hpd` embeds `struct hw_gpio base` and stores `hpd_registers`, shift, and mask tables. `HW_HPD_FROM_BASE` converts from `hw_gpio_pin` to `hw_hpd` via the embedded GPIO. `dal_hw_hpd_init` allocates/constructs a hardware HPD pin, and `dal_hw_hpd_get_pin` adapts a high-level `gpio` object back to the base pin interface.

Control flow: ASIC-specific factories or GPIO manager code create HPD pins, fill the register metadata, then expose only `hw_gpio_pin` operations to the rest of display core. The header is intentionally small because all behavior is in the C file and inherited common GPIO code.

State and persistence: state is inherited from `hw_gpio` plus immutable register table pointers after initialization. The header defines no persistence or synchronization.

Dependencies and integration: includes `hpd_regs.h`; forward-declared `struct gpio` is used for conversion from the GPIO wrapper. Integrates with hotplug interrupt handling and connector detection logic.

Risks and test signals: new ASIC HPD register definitions must keep shift/mask tables compatible with this struct. Compile tests should catch missing register fields; runtime tests should validate delayed sense bit mapping for each HPD instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_hpd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_translate.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_translate.c

Purpose: Dispatches GPIO offset/id translation initialization to the ASIC-generation-specific implementation for the active DCE/DCN version.

Important APIs and functions: `dal_hw_translate_init` accepts a `hw_translate`, `dce_version`, and environment, then assigns the proper function table by calling generation-specific initializers such as `dal_hw_translate_dce80_init`, `dal_hw_translate_dcn32_init`, or `dal_hw_translate_dcn42_init`.

Control flow: a single switch maps version enums to initialization functions. Several version groups share one translation implementation. Unsupported versions hit `BREAK_TO_DEBUGGER()` and return false. `CONFIG_DRM_AMD_DC_SI` conditionally includes and enables DCE6 support.

State and persistence: state is only the `translate->funcs` pointer initialized by the selected backend. The environment parameter is currently unused. No persistent state or register writes occur in this dispatcher.

Dependencies and integration: includes GPIO types, `hw_translate.h`, and all supported generation-specific translator headers. It sits between generic GPIO discovery and ASIC register-offset mapping used by GPIO factories/managers.

Risks and test signals: adding a new DCN version without updating this switch leaves GPIO translation unavailable. Tests should instantiate each supported `dce_version`, verify `funcs` is non-null, and cover build configurations with and without `CONFIG_DRM_AMD_DC_SI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_translate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_translate.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_translate.h

Purpose: Defines the abstract GPIO hardware translation interface. It converts between raw register offset/mask tuples and logical GPIO id/enable or `gpio_pin_info`.

Important APIs and types: `struct hw_translate_funcs` contains `offset_to_id` and `id_to_offset`. `struct hw_translate` holds a const function table. `dal_hw_translate_init` binds the correct implementation based on display engine version.

Control flow: callers initialize a `hw_translate` once, then call function pointers supplied by ASIC-specific backends. The interface supports two-way mapping for discovery and for constructing register metadata from logical GPIO identities.

State and persistence: only the function table pointer is stored. The translation itself is stateless and deterministic for a given ASIC generation.

Dependencies and integration: depends on `gpio_id`, `gpio_pin_info`, `dce_version`, and `dce_environment` definitions provided by includers. Used by GPIO manager/factory code that must abstract register layout differences.

Risks and test signals: invalid function table initialization will lead to null dereferences in callers. Tests should validate offset/id round trips for representative HPD/DDC/generic GPIO lines on each supported generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_translate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hdcp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hdcp/Makefile

Purpose: Adds the HDCP message transport object to the AMD display build.

Important APIs and build variables: `HDCP_MSG = hdcp_msg.o` names the object. `AMD_DAL_HDCP_MSG` prefixes it with `$(AMDDALPATH)/dc/hdcp/`. `AMD_DISPLAY_FILES += $(AMD_DAL_HDCP_MSG)` injects it into the display object list.

Control flow: this Makefile is included by the larger AMD display make hierarchy. There are no conditionals in this file, so inclusion depends on the parent build logic rather than local guards.

State and persistence: no runtime state. Build state is limited to make variables.

Dependencies and integration: integrates `hdcp_msg.c` with the display driver. It assumes `AMDDALPATH` and `AMD_DISPLAY_FILES` are defined by parent makefiles.

Risks and test signals: missing parent inclusion or wrong path prefix would silently omit HDCP message support. Build tests should confirm `hdcp_msg.o` appears in the final object list for configurations that enable AMD DC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hdcp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hdcp/hdcp_msg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hdcp/hdcp_msg.c

Purpose: Implements HDCP message transport for AMD display links. It maps HDCP 1.4/2.2 message ids to HDMI DDC/I2C offsets or DP DPCD AUX addresses, chooses transport by signal type, and retries failed transactions.

Important APIs and functions: `dc_process_hdcp_msg` is the public entry point returning `HDCP_MESSAGE_SUCCESS`, `FAILURE`, or `UNSUPPORTED`. `hdmi_14_process_transaction` builds DDC transactions to HDCP I2C addresses `0x3a/0x3b`. `dpcd_access_helper` chunks DPCD accesses by `DEFAULT_AUX_MAX_DATA_SIZE` and has special repeated handling for KSV FIFO reads. `dp_11_process_transaction` wraps DPCD access. `get_protection_properties_by_signal` maps signal/version to supported processing callbacks.

Control flow: the caller supplies signal, link, and message. The function validates message id, selects a protection backend by signal and HDCP version, attempts the transaction once, then retries up to `message_info->max_retries`. HDMI write transactions allocate a temporary buffer prepended with the register offset; HDMI reads use a two-payload offset-then-read command. DP transactions use DPCD address tables.

State and persistence: no long-lived state is stored. Transient heap memory is used only for HDMI writes and freed after submission. Hardware state changes happen at the sink over DDC/AUX.

Dependencies and integration: depends on `dm_helpers_submit_i2c`, `core_link_read_dpcd`, `core_link_write_dpcd`, link DPCD capabilities, and HDCP message type definitions. Integrated with the HDCP authentication state machine and link service.

Risks and test signals: HDCP 2.2 currently reuses HDMI/DP transport callbacks with TODO comments, so semantic coverage depends on message id tables being correct. KSV FIFO code logs errors for invalid sizes but continues. Tests should cover unsupported DP-VGA dongles, primary/secondary HDMI address selection, AUX chunking boundaries, retry counts, invalid message ids, and KSV FIFO lengths over 635 bytes or not divisible by five.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hdcp/hdcp_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/Makefile

Purpose: Adds HPO DP stream/link encoder objects for supported DCN generations to the AMD display build.

Important APIs and build variables: The whole file is guarded by `ifdef CONFIG_DRM_AMD_DC_FP`. It defines object groups for DCN31 (`dcn31_hpo_dp_stream_encoder.o`, `dcn31_hpo_dp_link_encoder.o`), DCN32 (`dcn32_hpo_dp_link_encoder.o`), and DCN42 (`dcn42_hpo_dp_link_encoder.o`), plus a DCN30 path that relies on `HPO_DCN30` being set externally.

Control flow: included by the parent make hierarchy, it appends generation-prefixed object paths to `AMD_DISPLAY_FILES` when floating-point DC support is enabled.

State and persistence: no runtime state. Build state is make variable composition.

Dependencies and integration: integrates the high-performance output encoders used for DP 2.x/128b132b paths. Relies on `AMDDALPATH`, `AMD_DISPLAY_FILES`, and generation-specific object variables.

Risks and test signals: object omission breaks HPO support only on affected ASICs/configurations. Build tests should verify `CONFIG_DRM_AMD_DC_FP=y` includes all intended generation objects and that DCN30's object variable is defined by the including context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.c

Purpose: Implements the DCN3.1 HPO DP link encoder for 128b/132b DisplayPort links. It controls link PHY enable/disable, test patterns, MST stream allocation table programming, VCP throttling, alt-mode detection, state readback, and VBIOS transmitter commands.

Important APIs and functions: `dcn31_hpo_dp_link_enc_enable` enables clocks, conditionally resets DPHY, enables precoder, and programs lane count. `dcn31_hpo_dp_link_enc_set_link_test_pattern` covers video, training, TPS, PRBS, custom 264-bit, and square patterns. `dcn31_hpo_dp_link_enc_update_stream_allocation_table` writes four SAT VC rows and triggers ACT/SAT update. `dcn31_hpo_dp_link_enc_set_throttled_vcp_size` converts fixed-point average slots to X/Y fields. `dcn31_hpo_dp_link_enc_enable_dp_output`, `disable_output`, and `set_ffe` call VBIOS transmitter control. `hpo_dp_link_encoder31_construct` binds the function table and register metadata.

Control flow: higher link code calls the `hpo_dp_link_encoder_funcs` vtable. PHY enable first uses BIOS to turn on transmitter output, then register programming enables link logic. MST allocation writes all four rows every update, zeroing unused entries, then waits for `SAT_UPDATE_PENDING` to clear. Disable uses BIOS transmitter disable and then shuts down encoder clocks.

State and persistence: object state includes instance, transmitter, HPD source, and register tables. Hardware state persists in DPHY, SAT, VC rate, and transmitter registers until changed. No heap allocation occurs.

Dependencies and integration: depends on `dc_bios_types.h`, `reg_helper.h`, `stream_encoder.h`, fixed-point helpers, MST allocation structs, and BIOS `transmitter_control`. Integrated with DP link training, MST payload manager, and HPO stream encoders.

Risks and test signals: invalid lane counts collapse to four-lane programming by ternary expression. Custom pattern code assumes at least 33 bytes. SAT wait timeout can leave MST allocation mismatched. Tests should cover each test pattern, lane-count encoding, VCP rounding carry, BIOS failure paths, MST table sizes 0-4, and alt-mode transmitter index bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h

Purpose: Declares DCN3.1 HPO DP link encoder register lists, field tables, concrete object layout, constructor, and exported helper functions.

Important APIs and types: `struct dcn31_hpo_dp_link_encoder` embeds `hpo_dp_link_encoder` and stores register, shift, and mask tables. `DCN3_1_HPO_DP_LINK_ENC_REG_LIST`, `REGS`, `MASK_SH_LIST`, and field-list macros define all DPHY/SAT/VC/test-pattern/RDPCSTX registers used by the implementation. Function declarations expose PHY control, test patterns, SAT updates, VCP size, state readback, FFE, and allocation-row fill.

Control flow: resource construction code expands the macros to create per-instance register tables, then calls `hpo_dp_link_encoder31_construct`. Runtime callers access behavior through the base vtable while generation-specific code can call helpers directly.

State and persistence: the struct stores immutable register metadata after construction and mutable base state for instance/transmitter/HPD. Register values persist in hardware.

Dependencies and integration: includes `link_encoder.h` and is consumed by DCN31 resources plus DCN32/DCN42 implementations that reuse the same concrete struct and many functions.

Risks and test signals: register/field macro drift can break multiple generations. Compile-time generated tables are the main guard; runtime state readback should be compared against writes for SAT, VC rate, link mode, and lane count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.c

Purpose: Implements the DCN3.1 HPO DP stream encoder. It controls DP2 stream reset/enable, blank/unblank sequencing, MSA/pixel-format programming, secondary data packets, DSC PPS packets, stream-to-link mapping, audio, and readback.

Important APIs and functions: `dcn31_hpo_dp_stream_enc_enable_stream` resets and enables the 32-symbol encoder. `dp_unblank` selects pixel source, enables video and FIFOs, and enables CRC. `dp_blank` disables video/SDP/FIFOs with a vblank-sized wait. `set_stream_attribute` maps CRTC timing, pixel encoding, color depth, color space, compressed flag, and DP MISC bits into pixel-format and MSA registers. `update_dp_info_packets`, `stop_dp_info_packets`, and `set_dsc_pps_info_packet` program VPG generic packets and SDP controls. Audio setup/enable/disable delegates to APG and manages SDP audio bits.

Control flow: the stream encoder vtable sequences enable, attribute programming, mapping to link encoder, unblank, info packet/audio updates, and eventual blank/disable. DSC PPS packets are split into four generic packet slots starting at index 11, while VSC/SPD/HDR/adaptive-sync use fixed packet indices.

State and persistence: object state stores context, BIOS pointer, instance, engine id, VPG/APG pointers, and register metadata. Hardware state includes stream enable, MSA registers, SDP packet enables, FIFO state, mapper target, and audio packet flags.

Dependencies and integration: depends on `dcn31_hpo_dp_stream_encoder.h`, `reg_helper.h`, `dc.h`, VPG, APG, timing/color structures, and DP infoframe definitions. Integrated with DP link programming, DSC, adaptive sync, HDR metadata, and audio routing.

Risks and test signals: interlaced modes break to debugger. MSA packing is bit-sensitive and depends on 8-bit lane fields. SDP stream disable must consider audio/GSP state to avoid cutting active packets. Tests should cover timing-to-MSA vectors, RGB/YCbCr/420/Y-only color cases, compressed DSC PPS enable/disable, adaptive-sync line numbers, audio with/without APG clock field, and mapper bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h

Purpose: Declares the DCN3.1 HPO DP stream encoder register schema, field masks, object layout, and constructor.

Important APIs and types: `struct dcn31_hpo_dp_stream_encoder` embeds `hpo_dp_stream_encoder` and stores register/shift/mask pointers. Register-list macros enumerate stream mapper, clock, input mux, audio, FIFO, SYM32 video, MSA, SDP, CRC, and HBLANK registers. Custom MSA lane field shift/mask definitions make generic `REG_SET_4` packing possible. DCN4.2 APG clock field macros extend the same struct.

Control flow: resource code expands macros into static register/field tables and calls `dcn31_hpo_dp_stream_encoder_construct`. Runtime code accesses operations through `hpo_dp_stream_encoder_funcs`.

State and persistence: struct state is mostly references to hardware metadata and owned base fields. The header itself defines no synchronization or persistence.

Dependencies and integration: includes DCN30 VPG, DCN31 APG, and `stream_encoder.h`. It bridges stream encoder core code with generation-specific packet/audio blocks.

Risks and test signals: incorrect macro expansion affects all stream operations. Compile tests should cover DCN31 and DCN42 field sets, and runtime readback should verify mapper, pixel format, SDP, and MSA registers after programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.c

Purpose: Provides the DCN3.2 HPO DP link encoder variant, largely reusing DCN3.1 behavior while supplying a DCN3.2 function table and alt-mode helper.

Important APIs and functions: `dcn32_hpo_dp_link_enc_is_in_alt_mode` reads `RDPCS_PHY_DPALT_DISABLE` from `RDPCSTX_PHY_CNTL6[transmitter]`. `hpo_dp_link_encoder32_construct` initializes the same `dcn31_hpo_dp_link_encoder` concrete struct but binds `dcn32_hpo_dp_link_encoder_funcs`.

Control flow: all major operations in the function table point to DCN31 implementations: PHY enable/disable, link enable/disable, test pattern, SAT table, throttled VCP, read state, and FFE. Only `is_in_alt_mode` is supplied locally.

State and persistence: base state and register metadata are initialized in the constructor. Hardware state is managed by reused DCN31 routines.

Dependencies and integration: includes DCN31 and DCN32 headers plus register helpers. Integrated by DCN32 resource construction for DP2/HPO links.

Risks and test signals: because it reuses DCN31 functions, register compatibility is assumed. Tests should verify DCN32 register tables include every field used by inherited routines and that alt-mode transmitter indexing is valid for UNIPHY A-E.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.h

Purpose: Declares DCN3.2-specific HPO DP link encoder field-mask list and constructor.

Important APIs and types: `DCN3_2_HPO_DP_LINK_ENC_MASK_SH_LIST` lists the fields needed by inherited DCN31 link encoder code, excluding the DCN31 RDPCSTX mask composition. `dcn32_hpo_dp_link_enc_is_in_alt_mode` and `hpo_dp_link_encoder32_construct` are declared.

Control flow: resource code uses this mask list when building DCN32 register metadata, then constructs a DCN32 function table over the DCN31 concrete object.

State and persistence: no state in the header. It defines metadata contracts for register field generation.

Dependencies and integration: includes `link_encoder.h` but uses `struct dcn31_hpo_dp_link_encoder` in prototypes, so includers must have the DCN31 definition available or rely on prior declarations.

Risks and test signals: the duplicate prototype for `dcn32_hpo_dp_link_enc_is_in_alt_mode` is harmless but noisy. Compile coverage should ensure include ordering provides the DCN31 struct, and register tests should validate field masks match DCN32 hardware headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.c

Purpose: Provides the DCN4.2 HPO DP link encoder variant. It reuses DCN31/DCN32 behavior and overrides state readback to match a three-stream/three-VC hardware shape.

Important APIs and functions: `dcn42_hpo_dp_link_enc_read_state` reads link enabled, lane count, mode, SAT VC0-VC2, and VC rate control 0-2. `hpo_dp_link_encoder42_construct` binds the DCN42 function table to a `dcn31_hpo_dp_link_encoder` object.

Control flow: function table entries mostly delegate to DCN31 implementations, with `is_in_alt_mode` using the DCN32 helper and `read_state` using the local reduced readback. Construction initializes context, instance, default HPD/transmitter unknowns, and register metadata.

State and persistence: same object state as DCN31/32. Hardware state is persistent in link encoder registers and read back on demand.

Dependencies and integration: includes DCN31/DCN32 link encoder headers, DCN42 header, register helpers, and stream encoder types. Integrated by DCN42 resource code.

Risks and test signals: inherited DCN31 allocation programming still writes four SAT rows, while DCN42 readback only reads three rows here; tests should confirm hardware supports or ignores the fourth row safely. Constructor and readback tests should validate DCN42 register tables and state arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.h

Purpose: Declares the DCN4.2 HPO DP link encoder constructor.

Important APIs and types: `hpo_dp_link_encoder42_construct` takes a `dcn31_hpo_dp_link_encoder` object plus context, instance, and DCN31-format register/shift/mask tables. It intentionally reuses the DCN31 concrete type for DCN42 behavior.

Control flow: resource construction code includes this header after DCN31 definitions and calls the constructor to bind the DCN42 vtable.

State and persistence: no state is defined here beyond constructor contracts.

Dependencies and integration: includes `link_encoder.h`, but prototypes refer to DCN31 link encoder structs, so include ordering matters. Integrated by DCN42 HPO resource setup.

Risks and test signals: the trailing include-guard comment names DCN32, a minor maintenance hazard. Compile tests should catch missing DCN31 declarations; runtime tests should validate the DCN42 vtable selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/Makefile

Purpose: Adds hubbub memory-arbiter/display-hub objects for multiple DCN generations to the AMD display build.

Important APIs and build variables: The object additions are guarded by `CONFIG_DRM_AMD_DC_FP`. It defines generation object lists for DCN10, DCN20, DCN201, DCN21, DCN30, DCN301, DCN31, DCN32, DCN35, DCN401, and DCN42, then appends prefixed paths to `AMD_DISPLAY_FILES`.

Control flow: parent makefiles include this file when building AMD DC. Each block maps one object name to a source-tree path under `$(AMDDALPATH)/dc/hubbub/<generation>/`.

State and persistence: no runtime state; build variables determine object inclusion.

Dependencies and integration: integrates all hubbub generation implementations with the display driver. Relies on parent-provided `AMDDALPATH`, `AMD_DISPLAY_FILES`, and config symbols.

Risks and test signals: missing an object breaks only the affected generation's memory hub programming. Build tests should check expected hubbub objects are present for FP-enabled DC builds and omitted when the guard is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.c

Purpose: Implements the base DCN1 hubbub, the display hub memory arbiter and address-aperture block. It programs watermarks, self-refresh/pstate controls, DCHUB frame-buffer windows, DCC capability decisions, soft reset, global timer, and state readback.

Important APIs and functions: `hubbub1_program_watermarks` composes urgent, stutter, and pstate watermark programming for sets A-D. `hubbub1_program_urgent_watermarks`, `stutter_watermarks`, and `pstate_watermarks` convert nanoseconds to refclk cycles and track pending lower-watermark updates. `hubbub1_update_dchub` programs local/ZFB/mixed AGP and FB apertures. `hubbub1_get_dcc_compression_cap` derives DCC block capability from format, swizzle, scan direction, and DET request sizing. `hubbub1_verify_allow_pstate_change_high` polls debug status and can force pstate allow as a hang avoidance workaround.

Control flow: callers use `hubbub_funcs` installed by `hubbub1_construct`. Watermark programming only lowers values when `safe_to_lower` is true; otherwise pending lower values are reported for later programming. DCC capability flow validates debug policy, pixel format, swizzle, request size, and DCC disable mode before filling output.

State and persistence: `dcn10_hubbub` stores cached watermarks and `debug_test_index_pstate`. Hardware state persists in arbiter, DCHUB, self-refresh, pstate, DCC-derived programming, and aperture registers. Static locals in pstate verification remember previous forced state and max sample.

Dependencies and integration: depends on `dcn10_hubp.h`, `dcn10_hubbub.h`, `reg_helper.h`, DCHUB/DCC structures, and DC debug flags. Integrated by resource pools as the base hubbub vtable and reused by later generations.

Risks and test signals: lowering-watermark rules can leave stale high values if caller misuses `safe_to_lower`. DCC logic mirrors DML and is sensitive to format/swizzle tables. Tests should cover all watermark sets, DCHUB framebuffer modes, DCC formats/swizzles/scan directions, pstate timeout workaround, and global timer/refdiv updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.h

Purpose: Defines the common hubbub register schema and DCN1 concrete hubbub object. Later generations extend this header's register and field lists.

Important APIs and types: `struct dcn_hubbub_registers` is a large register address table spanning DCN1 through newer fields. `struct dcn_hubbub_shift` and `struct dcn_hubbub_mask` aggregate field metadata macros. `struct dcn10_hubbub` embeds `struct hubbub`, register tables, debug pstate index, and cached watermarks. Macros define register lists for common, VM, SR watermark, DCN10, HVM, retention, DCN32, DCN35, DCN4.01, and DCN4.2 fields. Function declarations expose watermark, DCHUB, reset, timer, and aperture helpers.

Control flow: resource code expands generation-specific register macros into static tables. Constructors bind those tables to a concrete hubbub object and install a `hubbub_funcs` vtable.

State and persistence: the struct tracks cached software watermark values to enforce safe lowering and exposes register metadata for persistent hardware programming.

Dependencies and integration: includes `core_types.h` and `dchubbub.h`. It is included by DCN20/21/30 and later generation hubbub headers.

Risks and test signals: because the register struct accumulates fields across generations, shifts/masks must remain consistent with generation-specific register lists. Compile-time resource table generation plus runtime readback tests are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn20/dcn20_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn20/dcn20_hubbub.c

Purpose: Implements DCN2 hubbub extensions: VMID/page-table initialization, 48-bit system aperture programming, expanded DCC support, DCHUB reference-clock validation, watermarks with DCN2 request limits, and diagnostic readback.

Important APIs and functions: `hubbub2_init_dchub_sys_ctx` programs FB/AGP aperture and protection-fault default page, then initializes VMID0 when GART is present. `hubbub2_init_vm_ctx` configures per-VMID page tables. `hubbub2_update_dchub` updates ZFB/mixed/local apertures. `hubbub2_get_dcc_compression_cap` extends DCC to more formats and render swizzles. `hubbub2_get_dchub_ref_freq` validates global timer ref frequency. `hubbub2_program_watermarks` reuses DCN1 watermark helpers with pstate special-case lowering. `hubbub2_read_state` captures VM fault and debug state.

Control flow: `hubbub2_construct` installs the DCN2 function table. Initialization flows program physical aperture first, optionally VMID0, and return VMID capacity. Watermark programming follows DCN1 safe-lowering rules but adjusts outstanding request thresholds to DCN2 values.

State and persistence: `dcn20_hubbub` caches watermarks, detile buffer size, VMID objects, and generation tuning. Hardware state includes VM aperture/page tables, DCC capability-dependent programming, arbiter watermarks, fault status, and global timer state.

Dependencies and integration: depends on `dcn20_vmid`, `clk_mgr`, DC debug config, and common DCN1 hubbub helpers. Integrated by DCN2 resource pools and reused by DCN201/DCN21/DCN30.

Risks and test signals: `hubbub2_read_state` appears to assign LSB fault address into `vm_fault_addr_msb`, likely a typo. Reference clock outside 40-60 MHz asserts critically. Tests should cover VMID depth/block conversions, aperture programming for each framebuffer mode, DCC render swizzle exceptions, pstate support transitions, and VM fault readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn20/dcn20_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn20/dcn20_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn20/dcn20_hubbub.h

Purpose: Declares DCN2 hubbub register lists, masks, object layout, and public helpers.

Important APIs and types: `struct dcn20_hubbub` embeds `hubbub`, register metadata, cached watermarks, 16 VMID objects, detile/CRB/compbuf sizing, pixel chunk and DET sizes, and SDPIF rate-limit policy. `HUBBUB_REG_LIST_DCN20_COMMON`, `HUBBUB_REG_LIST_DCN20`, and `HUBBUB_MASK_SH_LIST_DCN20` add VM aperture/fault/protection registers to common hubbub fields. Prototypes expose VM context setup, DCHUB init/update, DCC helpers, reference clock readout, watermark readback, and full state readback.

Control flow: generation resource code expands the macros and calls `hubbub2_construct`. Runtime interactions happen through `hubbub_funcs` or exported helpers reused by later generations.

State and persistence: cached watermarks and VMID objects are software state; hardware state is in VM, watermark, and aperture registers.

Dependencies and integration: includes DCN10 hubbub and DCN20 VMID. It is the base struct reused by DCN201, DCN21, and DCN30 constructors.

Risks and test signals: `hubbub2_initialize_vmids` is declared with a DCC-like signature but not implemented in the read file set, suggesting stale declaration risk. Build and sparse checks should catch unused or mismatched declarations; VMID count tests should validate 16-entry bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn20/dcn20_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn201/dcn201_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn201/dcn201_hubbub.c

Purpose: Implements the DCN2.01 hubbub variant by reusing DCN2 DCHUB/DCC/readback helpers while installing a simplified watermark program path.

Important APIs and functions: `hubbub201_program_watermarks` programs urgent and pstate watermarks, SAT level, outstanding request threshold, and self-refresh control, but does not program stutter/SR watermark registers. `hubbub201_construct` binds the DCN201 function table and initializes common DCN20 fields.

Control flow: the DCN201 vtable uses `hubbub2_update_dchub`, DCC helpers, `hubbub2_wm_read_state`, `hubbub2_get_dchub_ref_freq`, and `hubbub2_read_state`, with VM context init callbacks set to NULL. Watermark programming follows the same safe-lowering behavior via DCN1 helper calls.

State and persistence: uses the `dcn20_hubbub` struct, cached watermarks, detile buffer size, and hardware arbiter registers. No VMID initialization state is managed through this vtable.

Dependencies and integration: depends on DCN20 hubbub helpers and register helpers. Integrated by DCN2.01 resource construction for generation-specific behavior.

Risks and test signals: NULL VM callbacks mean callers must branch by capability before invoking them. Tests should verify DCN201 resource code does not call missing VM init functions and that absence of stutter watermark programming matches hardware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn201/dcn201_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn201/dcn201_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn201/dcn201_hubbub.h

Purpose: Declares DCN2.01 hubbub register/mask lists and constructor.

Important APIs and types: `HUBBUB_REG_LIST_DCN201` includes common hubbub registers, VM watermark registers, and CRC control. `HUBBUB_MASK_SH_LIST_DCN201` includes common masks plus global timer refdiv. `hubbub201_construct` installs the generation-specific function table on a `dcn20_hubbub` object.

Control flow: resource code expands these macros for DCN201 static register metadata and calls the constructor during resource pool setup.

State and persistence: no unique state beyond the reused `dcn20_hubbub` object.

Dependencies and integration: includes `dcn20_hubbub.h`. Integrated by DCN201 resource creation.

Risks and test signals: reduced register coverage relative to DCN20 must match hardware. Build tests should ensure all fields used by `hubbub201_program_watermarks` exist in the generated tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn201/dcn201_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn21/dcn21_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn21/dcn21_hubbub.c

Purpose: Implements DCN2.1/Renoir hubbub behavior with host-VM/rIOMMU initialization, VM-row mirrored watermarks, request-throttling settings, and a generation workaround.

Important APIs and functions: `dcn21_dchvm_init` starts DCHVM host VM initialization, polls RIOMMU active, sets power status, requests prefetch, enables clock gating, and records `riommu_active`. `hubbub21_init_dchub` programs apertures, VMID0, and optionally runs RIOMMU prefetch. `hubbub21_program_urgent_watermarks`, `stutter_watermarks`, and `pstate_watermarks` write both base and VM-row watermark fields. `hubbub21_program_watermarks` sets SAT/outstanding/QOS thresholds and self-refresh control. `hubbub21_apply_DEDCN21_147_wa` rewrites urgency watermark A.

Control flow: constructor installs a vtable that reuses DCN2 update/DCC/refclock/readback helpers but uses DCN21 init and watermark functions. Watermark routines preserve safe-lowering semantics and return pending when lower values cannot yet be applied. DCHUB init skips RIOMMU prefetch when `skip_riommu_prefetch_wa` is set.

State and persistence: uses `dcn20_hubbub` cached watermarks and VMID state plus `hubbub->riommu_active`. Hardware state includes host VM/rIOMMU registers, VM-row watermark mirrors, QOS thresholds, and aperture registers.

Dependencies and integration: depends on Linux delay, DCN20 VMID/hubbub, and DC config flags. Integrated by DCN21 resource construction and memory-management paths.

Risks and test signals: some B/C/D stutter code writes VM_ROW_ALLOW_SR_EXIT_WATERMARK_A instead of B/C/D, and pstate B lowering sets `wm_pending = false`; both deserve review. Tests should cover RIOMMU polling timeout, skip-prefetch config, VMID0 base-address `| 1` hack, watermark mirror register selection, and DEDCN21_147 workaround execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn21/dcn21_hubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn21/dcn21_hubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn21/dcn21_hubbub.h

Purpose: Declares DCN2.1 hubbub host-VM register lists, masks, constructor, and watermark helpers.

Important APIs and types: `HUBBUB_HVM_REG_LIST` adds fractional urgency bandwidth, trip-to-memory, host VM control, DCHVM memory/clock/rIOMMU registers. `HUBBUB_MASK_SH_LIST_HVM` maps VM-row watermark and host VM fields. `HUBBUB_REG_LIST_DCN21` and `HUBBUB_MASK_SH_LIST_DCN21` combine DCN20 common registers, SR watermarks, HVM, VM fault fields, and refdiv. Prototypes expose DCHVM init, DCHUB init, watermark helpers/readback, and constructor.

Control flow: resource code expands macros into DCN21 register tables and calls `hubbub21_construct`. Runtime uses the installed vtable or helper calls from DCN30.

State and persistence: no new struct; DCN21 reuses `dcn20_hubbub` and base `hubbub` state while defining extra hardware metadata.

Dependencies and integration: includes DCN20 hubbub. Integrated by DCN21 and reused by DCN30 watermark programming.

Risks and test signals: field-list/mask mismatch can silently program wrong VM-row watermark fields. Compile-time generated table checks and hardware readback after programming are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn21/dcn21_hubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn30/dcn30_hubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn30/dcn30_hubbub.c

Purpose: Implements DCN3 hubbub behavior. It builds on DCN21 watermark programming, updates VM aperture initialization, extends DCC swizzle/control support, and adds force/readback utilities for watermark and pstate handling.

Important APIs and functions: `hubbub3_init_dchub_sys_ctx` programs system FB/AGP aperture and VMID0. `hubbub3_program_watermarks` delegates urgent/stutter/pstate programming to DCN21 helpers, sets SAT/outstanding thresholds, and conditionally updates self-refresh. `hubbub3_dcc_support_swizzle` supports standard, render, and display swizzle modes including non-X render variants. `hubbub3_get_dcc_compression_cap` fills newer DCC control bitfields. `hubbub3_force_wm_propagate_to_pipes`, `force_pstate_change_control`, `init_watermarks`, and `read_reg_state` provide operational/debug controls.

Control flow: constructor installs a DCN30 function table using DCN2 update/VM/readback helpers, DCN3 DCC helpers, DCN21 watermark readback, and DCN3 force utilities. Watermark programming mirrors DCN21 but only toggles self-refresh when lowering is safe or stutter is disabled.

State and persistence: uses `dcn20_hubbub` cached watermarks and VMID state; detile buffer is 184 KiB for DCN3. Hardware state includes VM apertures, DCC control decisions, watermarks, pstate force bits, DET/compbuf registers, and copied initial watermark sets.

Dependencies and integration: depends on `dcn30_hubbub.h`, DCN20 VMID setup, DCN21 watermark helpers, and register helper macros. Integrated by DCN30 resource pools.

Risks and test signals: DCC capability output changed to set control flags, so consumers must handle both legacy max block fields and new flags. Conditional self-refresh update can leave previous force state if callers do not prepare bandwidth correctly. Tests should cover DCC swizzle matrix, watermark initialization copy from set A to B-D, pstate force toggles, DET/compbuf readback, and system aperture/VMID0 programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn30/dcn30_hubbub.c -->

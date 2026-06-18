# subset-b-001394 Research

Grouped research for AMD display DCE audio, AUX, clock-source, DMCU, I2C, and IPP files. Each section is source-path aligned for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c

Purpose: implements the DCE Azalia/HDMI/DP audio hardware object behind `struct audio_funcs`. It programs indirect Azalia endpoint registers, advertises sink capabilities, filters audio sample-rate support by HDMI/DP blanking bandwidth, enables/disables audio and HBR capability, sets audio DTO clocks, validates endpoint presence, and allocates/destroys `struct dce_audio`.

Important APIs and functions: `dce_audio_create()` allocates the DCE wrapper and installs `funcs`; `dce_aud_hw_init()` initializes global codec capability/power-state registers on instance 0; `dce_aud_az_enable()`, `dce_aud_az_disable()`, and `dce_aud_az_disable_hbr_audio()` toggle endpoint hot-plug/audio/HBR fields; `dce_aud_az_configure()` writes speaker allocation, ACP support, audio descriptors, HBR support, lip-sync, sink IDs, port IDs, and display name; `dce_aud_wall_dto_setup()` programs HDMI DTO0 or DP DTO1. Static helpers cover indirect Azalia register access, ELD/audio format lookup, HDMI blanking math, DP SDP symbol budgeting, link-symbol-clock selection, latency clamping, and endpoint validity.

Control flow: configure starts by disabling endpoint clock gating, programs connection type based on `signal`, iterates every `AUDIO_FORMAT_CODE_*`, picks the highest-channel matching `audio_info->modes[]`, applies HDMI/DP bandwidth trimming for LPCM sample rates, writes one Azalia descriptor per format, then programs sink metadata and re-enables clock gating. DTO setup branches on HDMI TMDS versus DP-like signals and uses CRTC/pll info to program source, module, and phase registers.

State and persistence: state is hardware register state plus immutable object wiring (`regs`, `shifts`, `masks`, `base.funcs`). No filesystem persistence exists. The code mutates `sample_rates` local copies and endpoint registers; `audio_info` is read-only. Instance 0 performs one-time global codec initialization. Clock gating is temporarily disabled around Azalia endpoint writes.

Dependencies and integration: depends on `audio.h`, register helper macros, DCE 11 register definitions, fixed-point helpers, DC signal/color/link types, CRTC timing and DP link data supplied by link/stream programming. It integrates with the DC resource pool as the implementation of audio callbacks consumed by stream/link enable paths.

Risks and test signals: bandwidth math is unit-sensitive (`100Hz`, kHz, symbols, margins) and should be tested with HDMI low-blanking modes, DP MST, 128b/132b links, DSC, YCbCr 4:2:0/4:2:2, and deep color. `dce_aud_az_configure()` assumes non-null `audio_info` for most paths and directly indexes an 18-character display name, so malformed ELD inputs are a risk. Useful validation signals are correct ELD exposure to ALSA, HBR enable only when 192 kHz 8-channel fits, no audio loss after hotplug, DTO register traces, and suspend/resume audio recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h

Purpose: declares the DCE audio hardware wrapper and the register/mask/shift lists used by ASIC-specific resource construction. It exposes construction, destruction, initialization, Azalia enable/disable/configure, and wall DTO setup entry points for the DCE audio implementation.

Important APIs and types: `AUD_COMMON_REG_LIST()` lists Azalia endpoint, codec parameter, and DCCG audio DTO registers. `AUD_COMMON_MASK_SH_LIST_BASE()`, `AUD_COMMON_MASK_SH_LIST()`, and optional `AUD_DCE60_MASK_SH_LIST()` generate bitfield metadata. `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` carry addresses and field encodings. `struct dce_audio` embeds `struct audio base` and points to those metadata tables. Public functions include `dce_audio_create()`, `dce_aud_destroy()`, `dce_aud_hw_init()`, `dce_aud_az_enable()`, `dce_aud_az_disable()`, `dce_aud_az_disable_hbr_audio()`, `dce_aud_az_configure()`, and `dce_aud_wall_dto_setup()`.

Control flow and integration: this header is consumed by resource builders that instantiate audio blocks with ASIC-specific register tables, and by `dce_audio.c` to downcast from `struct audio` to `struct dce_audio`. The header does not implement behavior; it defines the ABI between generic DC audio code and DCE-specific register programming.

State and persistence: the only persistent state described here is in-memory object state and hardware register metadata. There is no external persistence. Correctness depends on matching each ASIC's generated register list with the mask/shift list selected at compile/resource-build time.

Dependencies and risks: depends on `audio.h` for base interfaces and audio data structures. Risks are primarily table mismatch risks: a wrong register list, missing optional DTO 512-FBR fields, or DCE60 mask divergence can make the implementation write incorrect fields. Test signals include successful resource construction for each DCE/DCN generation, non-null audio callbacks, register programming traces matching expected addresses, and compile coverage for `CONFIG_DRM_AMD_DC_SI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.c

Purpose: implements native DCE DisplayPort AUX and I2C-over-AUX transactions, plus retry policy and optional DMUB forwarding. It owns AUX engine acquisition, register programming, request/reply packing, timeout configuration, and high-level retry semantics for DPCD/EDID/DDC service operations.

Important APIs and functions: `dce110_aux_engine_construct()` initializes `struct aux_engine_dce110`; `dce110_aux_engine_acquire()` is the public acquire wrapper; `dce_aux_transfer_raw()` performs a native AUX request; `dce_aux_transfer_dmub_raw()` configures the DDC channel then delegates to `dm_helper_dmub_aux_transfer_sync()`; `dce_aux_transfer_with_retries()` is the main caller-facing retry loop. Static helpers implement `acquire_engine()`, `release_engine()`, request composition, reply parsing, AUX status classification, configurable timeout programming, payload logging, and AUX action selection from `struct aux_payload`.

Control flow: raw transfer validates the DDC pin, selects the engine from `res_pool->engines[pin_data->en]`, acquires GPIO/AUX ownership, maps payload to AUX or I2C-over-AUX action, writes command/address/length/data into AUX SW registers, starts the transaction, polls status, reads reply bytes on success, logs request/reply events, and releases ownership. The retry wrapper chooses native versus DMUB based on debug flags or missing `ddc_pin`, then handles ACK, ACKM, AUX/I2C defers, NACKs, invalid replies, HPD disconnects, engine-acquire failures, and timeout retry budgets.

State and persistence: persistent state is in hardware arbitration/control/status registers and `struct dce_aux` fields such as `ddc`, `delay`, `max_defer_write_retry`, `polling_timeout_period`, and optional timeout callback. The retry loop mutates `payload` for write-status-update polling after AUX ACKM, temporarily installs a local reply byte if none was provided, and restores `payload->reply` on failure.

Dependencies and integration: depends on DDC/GPIO services, DC resource pool AUX engines, `dm_helpers` for DMUB AUX, event logging, DP AUX transaction enums, and register helper macros. Integrates with link detection, DPCD reads/writes, EDID over AUX, USB4/DPIA handling, and debug-controlled legacy-DMUB AUX routing.

Risks and test signals: high risk areas are timeout unit conversion, defer accounting (`defer_time_in_ms`), mutation of caller payloads during ACKM handling, DDC pin to engine indexing, HPD-low early exits, and optional timeout field availability. Test with native AUX, DMUB AUX, I2C-over-AUX EDID, repeated DEFER, invalid reply, timeout, HPD disconnect, USB4 DPIA, and configurable timeout paths. Useful signals are DPCD read stability, no stuck AUX arbitration, retry logs, event-log payloads, and successful hotplug/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.h

Purpose: defines the DCE AUX engine object, register tables, mask/shift field lists, timeout constants, construction data, public native/DMUB transfer entry points, and small AUX function table used by higher-level DDC service code.

Important APIs and types: `AUX_COMMON_REG_LIST0()` and `AUX_COMMON_REG_LIST()` enumerate per-engine AUX registers and optional impedance calibration registers. `DCE_AUX_REG_FIELD_LIST()` plus DCE10/DCE/DCE12/DCN mask-list macros generate field metadata for multiple register namespaces. `struct dce_aux` stores instance, current DDC, context, delay/defer tuning, acquire-reset flag, and `struct dce_aux_funcs`. `struct aux_engine_dce110` embeds `dce_aux` and adds register/mask/shift tables plus cached register addresses and `polling_timeout_period`. Public functions include constructor/destructor/acquire, `dce_aux_transfer_raw()`, `dce_aux_transfer_dmub_raw()`, and `dce_aux_transfer_with_retries()`.

Control flow and integration: the header provides the contract used by resource pools to create AUX engines and by DDC service/link code to issue AUX payloads. Optional `configure_timeout` is installed only when the ASIC supports external AUX timeout configuration; otherwise callers must use default timing.

State and persistence: no external persistence. State is per-engine in memory and in AUX hardware registers. The register lists must match the generated ASIC register definitions, especially the presence or absence of `AUX_RESET`, `AUX_DPHY_RX_CONTROL1`, and impedance calibration fields.

Dependencies and risks: depends on GPIO service and `inc/hw/aux_engine.h`. Risks include mask-list duplication across DCE12/DCN variants, optional fields being zero on older hardware, and timeout constants being used as both hardware and software poll budgets. Test signals include successful compile/resource construction for all supported ASIC families, correct callback installation for timeout-configurable AUX engines, and validation that native/DMUB transfer entry points are reachable from DDC service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.c

Purpose: implements DCE/DCN clock-source callbacks for pixel clock divider calculation, spread-spectrum handling, VBIOS pixel-clock programming, DP DTO programming, pixel-clock readback, power-down, and construction of generation-specific clock-source function tables.

Important APIs and functions: constructors `dce110_clk_src_construct()`, `dce112_clk_src_construct()`, `dcn20_clk_src_construct()`, `dcn3_clk_src_construct()`, `dcn301_clk_src_construct()`, `dcn31_clk_src_construct()`, and `dcn401_clk_src_construct()` initialize base callbacks and metadata. `dce110_get_pix_clk_dividers()`, `dce112_get_pix_clk_dividers()`, and `dcn3_get_pix_clk_dividers()` fill `struct pll_settings`. Program callbacks include `dce110_program_pix_clk()`, `dce112_program_pix_clk()`, `dcn20_program_pix_clk()`, `dcn3_program_pix_clk()`, `dcn31_program_pix_clk()`, and `dcn401_program_pix_clk()`. Static helpers calculate PLL feedback/fractional dividers, adjust pixel clocks via BIOS, read ATOMBIOS spread-spectrum tables, compute delta-sigma spread data, program resync/deep-color registers, and look up video-optimized 1000/1001 rates.

Control flow: legacy DCE110 uses BIOS-adjusted clocks, searches PLL divider ranges within widening tolerance, optionally disables/enables PPLL spread spectrum, calls BIOS `set_pixel_clock`, then programs deep-color resync. DCE112/DCN mostly delegates rate programming to BIOS for TMDS/HDMI while DP DTO sources use external/reference clocks. DCN3/DCN31 and DCN401 directly program DP DTO phase/modulo for DP/virtual or all non-TMDS signals, optionally using the video-optimized rate table, and call BIOS only for TMDS/HDMI cases.

State and persistence: state is held in `struct dce110_clk_src`: BIOS pointer, register metadata, spread-spectrum arrays allocated from ATOMBIOS data, external/reference clock rates, and PLL calculator configuration. Register state persists in hardware until reprogrammed. The file does not free spread-spectrum arrays here, so lifetime is tied to resource teardown outside this file.

Dependencies and integration: depends on DC BIOS callbacks (`adjust_pixel_clock`, `set_pixel_clock`, spread-spectrum queries), clock manager (`dprefclk_khz`, `dp_dto_source_clock_in_khz`), DCCG DTO callback on DCN401, register helpers, fixed-point math, and stream pixel clock parameters from pipe programming. It implements `struct clock_source_funcs` consumed by the DC resource and hardware sequencing layers.

Risks and test signals: highest risks are unit mismatches (`100Hz`, kHz, Hz), overflow/rounding in PLL/DTO math, invalid ATOMBIOS SS data, DP 128b/132b DTO source selection, HDMI deep-color adjustments, YCbCr420 double-rate, and the unconditional true return in some DCN program wrappers after delegated calls. Test with HDMI 24/30/36/48 bpp, DP SST/MST, eDP with spread-spectrum DP ref clock, vblank synchronization readback, 1000/1001 video rates, >600 MHz TMDS rejection on DCN401, and BIOS failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.h

Purpose: declares the DCE/DCN clock-source wrapper, register/mask/shift lists for PLL resync and DP DTO programming, constructors for several hardware generations, and the video-optimized pixel-rate table interface.

Important APIs and types: `TO_DCE110_CLK_SRC()` downcasts `struct clock_source`. Register-list macros cover DCE PLL/resync registers and DCN1/DCN2/DCN3/DCN401 DTO phase/modulo/pixel-rate-control layouts. `struct dce110_clk_src_regs`, `struct dce110_clk_src_shift`, and `struct dce110_clk_src_mask` describe register metadata. `struct dce110_clk_src` embeds `struct clock_source`, BIOS pointer, spread-spectrum arrays for DP/HDMI/DVI/LVDS, external/reference clocks, and two PLL calculator objects. Constructors select function tables by generation. `struct pixel_rate_range_table_entry` and `look_up_in_video_optimized_rate_tlb()` expose 1000/1001 rate mapping.

Control flow and integration: resource builders include this header to construct clock sources with ASIC-specific register tables. The generic clock-source API then calls the function table set by the constructor. The header is the generation-compatibility surface between DC resource construction, BIOS programming, and `dce_clock_source.c`.

State and persistence: describes in-memory state only; hardware state is programmed by the C file through supplied register addresses. Spread-spectrum pointers and counts persist for the lifetime of the clock-source object.

Dependencies and risks: depends on `../inc/clock_source.h`, `MAX_PIPES`, BIOS/clock-source types, and generated register macros. Risks center on maintaining many generation-specific register list macros; a wrong `pllid`/pipe index mapping can route DTO programming to the wrong pipe. Compile-time coverage across ASIC families and runtime register tracing for each constructor are key test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_dmcu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_dmcu.c

Purpose: implements DCE/DCN Display Microcontroller Unit callbacks for initialization, IRAM access, Panel Self Refresh control, firmware/version handling, backlight fractional PWM, PHY synchronization, EDID CEA messaging, and optional secure-display CRC window forwarding.

Important APIs and functions: creators `dce_dmcu_create()`, `dcn10_dmcu_create()`, `dcn20_dmcu_create()`, and `dcn21_dmcu_create()` allocate a `struct dce_dmcu` and install generation-specific `dmcu_funcs`. DCE paths include `dce_dmcu_load_iram()`, `dce_dmcu_setup_psr()`, `dce_dmcu_set_psr_enable()`, PSR state/wait-loop helpers, and initialization checks. DCN10 adds stateful initialization from `DC_DMCU_SCRATCH`, version reads from IRAM, fractional PWM control, IRAM init notification, extended PSR setup with SMU optimization, EDID CEA send/receive helpers, and optional secure-display CRC commands. DCN20/21 add PHY lock/unlock and PSP/auto-load gating.

Control flow: command paths wait for `MASTER_COMM_INTERRUPT` to clear, write command data registers, set `MASTER_COMM_CMD_REG_BYTE0`, then assert `MASTER_COMM_INTERRUPT` and often wait for it to clear again. PSR setup also programs link encoder fast training and secondary packet timing before handing packed config unions to firmware. DCN init reads firmware state from scratch, initializes ramping/PWM and USB-C transmitter interrupt masks when firmware is loaded but uninitialized, then caches version and state.

State and persistence: state spans hardware scratch/command/IRAM registers and `struct dmcu` fields such as `dmcu_state`, `dmcu_version`, `cached_wait_loop_number`, `auto_load_dmcu`, and `psp_version`. No filesystem persistence exists. Wait-loop caching avoids redundant firmware commands. IRAM access toggles host access and auto-increment bits and relies on memory-power-state waits.

Dependencies and integration: depends on link encoder PSR functions, DC link list, DC config flags, SMU interrupt control, register helpers, PSP scratch registers, and optional secure display config. It implements the `dmcu_funcs` table used by ABM/PSR/link power features in the DC stack.

Risks and test signals: risks include command mailbox deadlocks, high-IRQ PSR waits requiring `udelay` instead of sleeping, IRAM power-state timeout assumptions, `dcn10_send_edid_cea()` packing eight bytes while only validating `length <= 8` and then reading `data[4..7]`, PSP version gate regressions, and generation-specific scratch semantics. Test PSR enter/exit, firmware unloaded/uninitialized/running states, suspend/resume, fractional PWM toggles, USB-C interrupt mask formation, PHY lock/unlock, EDID CEA ACK/NACK, and secure-display builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_dmcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_dmcu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_dmcu.h

Purpose: defines DCE/DCN DMCU register lists, mask/shift field lists, the `struct dce_dmcu` wrapper, PSR command-data packing unions, and constructors/destructor for generation-specific DMCU implementations.

Important APIs and types: register-list macros cover DCE base, DCE60, DCE80, DCE110, DCN10, and DCN20 register sets. `DMCU_REG_FIELD_LIST()` generates shift/mask structs. `struct dce_dmcu_registers` contains DMCU control/status, IRAM access, master/slave mailbox, interrupt, scratch, and memory-power registers. `struct dce_dmcu` embeds `struct dmcu`. PSR unions `dce_dmcu_psr_config_data_reg1/2/3` and `dce_dmcu_psr_config_data_wait_loop_reg1` define the exact mailbox bit layout for firmware commands.

Control flow and integration: the header is used by ASIC resource files to pass correct register tables into `dce_dmcu.c`. Generic DC code sees only `struct dmcu` and its function table, while this header preserves the DCE-specific packing contract required by DMCU firmware.

State and persistence: no external persistence. The object persists context, function table, cached wait loop, firmware state/version fields inherited from `struct dmcu`, and register metadata. Mailbox union layouts are persistent ABI with DMCU firmware and must not drift.

Dependencies and risks: depends on `dmcu.h` and generated register names. Risks include bitfield layout portability/ABI assumptions, comments that mention a mismatched closing guard (`_DCE_ABM_H_`), and generation macros omitting fields used by newer code paths. Test signals include compile coverage for SI/non-SI configs, PSR command binary compatibility, DMCU construction on DCE/DCN families, and register table validation for optional `DMCUB_SCRATCH15`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_dmcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c.c

Purpose: provides the top-level DCE I2C dispatcher and OEM-I2C presence helper. It chooses hardware I2C when available and falls back to software GPIO bit-banging when the hardware engine is unavailable.

Important APIs and functions: `dce_i2c_oem_device_present()` checks BIOS firmware metadata for an OEM I2C object, fetches its I2C info through `dc_bios->funcs->get_i2c_info()`, and compares the slave address. `dce_i2c_submit_command()` validates inputs, attempts `acquire_i2c_hw_engine()`, submits through `dce_i2c_submit_command_hw()` on success, otherwise initializes a stack `struct dce_i2c_sw`, acquires the DDC in software mode, and submits through `dce_i2c_submit_command_sw()`.

Control flow: the dispatcher returns false on null DDC/command, uses the DDC's context/resource pool to find hardware engines, and only tries software acquisition after hardware acquisition fails. Hardware and software submission functions own release/close behavior after acquisition.

State and persistence: no persistent state is stored here. It creates a temporary software-engine struct and relies on lower layers to update hardware engine/DDC state and resource-pool flags.

Dependencies and integration: depends on `dce_i2c.h`, `dce_i2c_hw.h`, `dce_i2c_sw.h`, DC BIOS, resource pool, DDC service, and register/helper macros. It is the generic DC I2C entry point used by DDC/EDID and display-management flows.

Risks and test signals: risks are acquisition/release ownership mismatches between hardware and software paths, null `ddc->ctx` assumptions, and hardware fallback behavior when `pool->i2c_hw_buffer_in_use` is set. Test with hardware-supported DDC, hardware-busy fallback, invalid inputs, BIOS OEM I2C object present/missing, and repeated EDID reads after fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c.h

Purpose: declares the top-level DCE I2C helper functions and includes both hardware and software engine interfaces so callers can submit I2C commands without selecting the backend directly.

Important APIs: `dce_i2c_oem_device_present()` reports whether a BIOS-advertised OEM I2C device matches a slave address on a DDC service. `dce_i2c_submit_command()` submits a `struct i2c_command` against a `struct ddc`, internally choosing hardware I2C or software bit-banging.

Control flow and integration: this header is included by DDC/display code and by the backend implementations. It forms the small public façade over `dce_i2c_hw.c` and `dce_i2c_sw.c`.

State and persistence: no state is declared besides the function contracts. Backend state is in `struct dce_i2c_hw`, `struct dce_i2c_sw`, GPIO/DDC objects, and resource-pool flags.

Dependencies and risks: depends on `inc/core_types.h`, `dce_i2c_hw.h`, and `dce_i2c_sw.h`. The main maintenance risk is exposing backend structs through the façade include, which couples users to backend type definitions. Test signals are successful compilation of callers with both backends and runtime coverage of backend fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.c

Purpose: implements hardware-assisted I2C transactions for DCE/DCN DDC lines. It handles engine arbitration, GPIO DDC open/close, setup/reset/speed programming, transaction descriptor and circular-buffer programming, status polling, reply extraction, release workarounds, and generation-specific construction defaults.

Important APIs and functions: `acquire_i2c_hw_engine()` maps a DDC line to `pool->hw_i2cs[]`, opens it in hardware mode, sets up the engine, and marks `pool->i2c_hw_buffer_in_use`. `dce_i2c_submit_command_hw()` sets speed, iterates payloads, submits each with MOT awareness, clears the pool flag, releases the engine, closes DDC, and nulls `ddc`. Static helpers include `execute_transaction()`, `get_channel_status()`, `process_transaction()`, `process_channel_reply()`, `set_speed()`, `setup_engine()`, `release_engine()`, and `cntl_stuck_hw_workaround()`. Constructors tune buffer size, default speed, setup limit, and send-reset length for DCE100/DCE112/DCN1/DCN2.

Control flow: acquisition rejects null/unsupported DDC, out-of-range lines, global buffer contention, and DMCU/HW-owned engines. Setup deasserts reset, optionally powers I2C memory, enables clock fields, arbitrates SW access, selects the DDC line, programs time limit/reset length, and default speed. Payload submission checks buffer capacity, builds transaction registers, writes address/data bytes, starts the transaction when the last/MOT boundary is reached, waits until status changes from busy, and reads data for read payloads.

State and persistence: persistent state includes `engine_keep_power_up_count`, `transaction_count`, `buffer_used_bytes`, `buffer_used_write`, `ddc`, speed/reference parameters, and resource-pool `i2c_hw_buffer_in_use`. Hardware register state controls arbitration, memory power, reset, speed, buffer indexes, and transaction count.

Dependencies and integration: depends on resource pool, GPIO/DDC service, DC caps/debug flags, generated register metadata, and I2C command/payload structures. It is selected by `dce_i2c_submit_command()` when the DDC line advertises hardware support.

Risks and test signals: risks include the global buffer flag not being cleared on unexpected paths, buffer accounting after read payloads, speed/prescale divide behavior, reset safety when the engine is not SW-owned, DMCU-only arbitration, low-power memory wake/sleep, and the stuck-control workaround. Test with multi-payload MOT reads/writes, payloads near buffer limit, HDCP speed restore, VBios/DDC contention, DCN reset-length debug flag, memory low-power enabled, and repeated hotplug EDID reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.h

Purpose: defines hardware I2C status/action enums, timing/buffer constants, register/mask/shift metadata, transaction data, hardware-engine state, constructors, and public hardware submit/acquire functions.

Important APIs and types: enums describe I2C arbitration/status, operation results, and DCE transaction actions including normal and MOT reads/writes plus DP/DPCD actions. Constants define setup limits, buffer sizes, default speeds, reset lengths, and timeout clocks. `I2C_HW_ENGINE_COMMON_REG_LIST*()` and mask-list macros provide generation-specific register metadata. `struct i2c_request_transaction_data` is the internal request descriptor. `struct dce_i2c_hw` stores DDC pointer, transaction/buffer counters, frequency/defaults, engine id, setup/reset parameters, context, and register metadata. Public functions construct generation variants, submit hardware commands, and acquire an engine.

Control flow and integration: resource builders allocate one `dce_i2c_hw` per DDC-capable line and initialize it with this header's constructors. `dce_i2c.c` acquires and submits through the public functions. The header also shares `i2c_request_transaction_data` with the software backend for common request action/status meanings.

State and persistence: in-memory state persists across command submissions in the resource pool; hardware register state is managed by `dce_i2c_hw.c`. The `engine_keep_power_up_count` influences whether the engine is disabled during release.

Dependencies and risks: depends on generated register names, `struct ddc`, `struct resource_pool`, and DC context definitions from included compile units. Risks are enum value compatibility with hardware register encodings, optional DCN memory-power/clock-enable fields, and buffer-size differences by generation. Test signals include constructor defaults per ASIC, compile coverage for DCN30/DCN35/DCN401 mask lists, and acquisition/submission behavior under hardware contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_sw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_sw.c

Purpose: implements the software I2C fallback engine by bit-banging DDC GPIO clock/data pins. It supports multi-payload I2C commands, repeated starts for MOT transactions, ACK/NACK handling, clock-stretch waits, stop/start generation, and DDC acquisition/release.

Important APIs and functions: `dce_i2c_sw_construct()` stores context; `dce_i2c_engine_acquire_sw()` retries opening the DDC in fast-output I2C GPIO mode; `dce_i2c_submit_command_sw()` sets speed, submits each payload, and releases. Static helpers read/write SDA/SCL, wait for SCL high, write/read bytes MSB-first, generate start/stop, submit a channel request, and map `struct i2c_payload` to `i2c_request_transaction_data`.

Control flow: acquisition opens GPIO pins; command submission computes `clock_delay = max(1000/speed, 12)` and loops payloads with MOT true except the last. Each payload generates start/repeated-start, writes address and data or address then reads bytes, ACKs all but the last read byte, and sends stop on non-MOT or failure. Status becomes succeeded or failed in the request descriptor, and any failed payload aborts the command.

State and persistence: state is transient in `struct dce_i2c_sw`: active `ddc`, context, speed, and clock delay. GPIO pin electrical state is modified during transactions, then `dal_ddc_close()` releases ownership and clears `engine->ddc`.

Dependencies and integration: depends on GPIO service DDC APIs, I2C command/payload structures, and the action/status enums from the hardware header. It is used by the top-level DCE I2C dispatcher when hardware acquisition fails.

Risks and test signals: risks include timing accuracy under `udelay`, clock-stretch timeout scaling by `clock_delay_div_4`, minimum delay behavior for high requested speeds, SDA stuck-low start retries, stop failure handling, and ensuring release after all failure paths. Test with EDID reads, write-then-read repeated starts, slow clock-stretching sinks, NACKing addresses, hardware-busy fallback, and high CPU load where bit-bang timing is stressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_sw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_sw.h

Purpose: declares the software I2C fallback engine state, default timing constants, constructor, command submitter, and acquisition function.

Important APIs and types: constants set the default 50 kHz software I2C speed, 10 start retries, and 3000-unit timeout delay. `struct dce_i2c_sw` stores the current DDC, DC context, calculated clock delay, and selected speed. `dce_i2c_sw_construct()` initializes the context, `dce_i2c_engine_acquire_sw()` opens the DDC pins for bit-banging, and `dce_i2c_submit_command_sw()` executes a full `struct i2c_command`.

Control flow and integration: included by the top-level I2C facade and software backend. The software engine is usually stack-allocated by `dce_i2c_submit_command()` after hardware acquisition fails, then acquired and submitted through these declarations.

State and persistence: no external persistence. The active DDC pointer exists only while the software engine owns GPIO pins; the C file clears it during release.

Dependencies and risks: relies on `struct ddc`, `struct dc_context`, `struct resource_pool`, and `struct i2c_command` definitions from surrounding DC headers. Timing constants are hardware/protocol sensitive and should be validated with slow or clock-stretching sinks. Test signals are successful fallback EDID reads, repeated-start transactions, and clean DDC release after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_sw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_ipp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_ipp.c

Purpose: implements DCE input pixel processor callbacks for hardware cursor programming, prescale, legacy input LUT programming, degamma mode selection, construction, and destruction.

Important APIs and functions: `dce_ipp_construct()` installs `dce_ipp_funcs`; optional `dce60_ipp_construct()` installs a SI-specific degamma function; `dce_ipp_destroy()` frees the object. Callback implementations include `dce_ipp_cursor_set_position()`, `dce_ipp_cursor_set_attributes()`, `dce_ipp_program_prescale()`, `dce_ipp_program_input_lut()`, and `dce_ipp_set_degamma()`/`dce60_ipp_set_degamma()`.

Control flow: cursor position locks update registers, toggles enable, writes position and hotspot, then unlocks. Cursor attributes locks, maps cursor format to hardware mode, writes magnification/transparent-clamp flags, programs mono colors when needed, writes width/height as size minus one, writes high address before low address, and unlocks. Prescale first bypasses, writes RGB scale/bias, then enables prescale and bypasses legacy LUT if requested. Input LUT powers LUT memory when available, enables RGB writes, selects 256-entry mode and u0.12 format, streams red/green/blue values from `struct dc_gamma`, powers memory down, bypasses prescale, and enables legacy LUT. Degamma writes graph/cursor degamma modes.

State and persistence: persistent state is register state plus object metadata (`ctx`, `inst`, `regs`, `ipp_shift`, `ipp_mask`). No filesystem persistence. Cursor register locking prevents partial visible updates. LUT programming consumes `gamma->num_entries` without local clamping, so caller-provided table size must match hardware expectations.

Dependencies and integration: depends on `dce_ipp.h`, register helpers, fixed-point rounding through gamma entries, and generic `input_pixel_processor` callbacks used by plane/cursor/color programming.

Risks and test signals: risks include cursor size underflow if width/height are zero, invalid cursor modes falling back after debugger break, address programming order requirements, LUT memory-power polarity, and gamma entry counts exceeding hardware LUT depth. Test cursor formats/positions/hotspots, 4K-aligned cursor addresses above 32 bits, prescale plus LUT interactions, sRGB/bypass degamma, SI builds, and visual gamma/cursor validation after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_ipp.c -->

# subset-b-001463 research

This grouped report covers AMD display DMUB hardware service code for DCN 3.1 through DCN 4.2 register layouts, DMUB register helpers, the DMUB service core/stat path, and adjacent display type headers. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.h

Purpose: declares the DCN 3.1 DMUB register layout and hardware-operation API used by the DMUB service layer. The register macro inventory covers DMCUB control/reset/security, inbox0/inbox1 and outbox0/outbox1 mailbox registers, code-window region3 offsets/base/top registers, region4/5 mappings, scratch registers, GPINT, pipe-support, MMHUBBUB soft reset, framebuffer base/offset, timer, fault addresses, and GPINT interrupt enable/ack fields.

Important APIs and control flow: `DMUB_DCN31_REGS()` and `DMUB_DCN31_FIELDS()` are expanded by ASIC-specific `.c` files to build `struct dmub_srv_dcn31_regs`, which contains offset, mask, and shift tables consumed by `dmub_reg.h` macros. The declared functions form the DCN31 hardware vtable: reset/release, backdoor firmware load, window/mailbox setup, mailbox pointer access, support/init detection, PSR-SU capability, GPINT command/ack/response/dataout, boot option scratch programming, outbox0 trace setup, current time, diagnostic capture, and detection-required status.

State and persistence behavior: the header owns no runtime state, but fixes the persistent register ABI between generated DCN offset headers, the static `dmub_srv_dcn31_regs` table, and `struct dmub_srv` function pointers. Runtime state persists in hardware registers and DMUB scratch fields; software state is maintained by `dmub_srv.c` after calling these callbacks.

Dependencies and integration points: depends on `dmub_dcn20.h`, `dmub_cmd` types reachable through lower headers, and the per-ASIC generated DCN offset/mask headers that provide field names. `dmub_srv_hw_setup()` assigns this API for DCN31/DCN31B/DCN314/DCN315/DCN316, sometimes replacing only the register table or PSR-SU predicate.

Risks and test signals: risks include macro drift between `DMUB_DCN31_REGS()` and generated DCN headers, missing field definitions causing compile failures, scratch-register ABI changes breaking boot status/options, and unlocked outbox pointer access relying on the documented stat-only path. Test signals include successful build for every DCN31-family ASIC, DMUB boot reaching `dal_fw`, inbox/outbox pointer movement, GPINT stop/reset completion, PSR-SU gating on supported firmware, and populated diagnostics after timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c

Purpose: instantiates the DCN 3.1.4 DMUB register table using DCN 3.1 common register/field macros with the `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h` generated register definitions. It also provides the DCN314-specific PSR-SU firmware capability check.

Important APIs and control flow: `dmub_srv_dcn314_regs` expands `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN31_FIELDS()` into concrete offsets, masks, and shifts using fixed segment base constants. `dmub_dcn314_is_psrsu_supported()` returns true only when `dmub->fw_version >= DMUB_FW_VERSION(8, 0, 16)`.

State and persistence behavior: no mutable software state is stored here. The exported const table is shared by all DCN314 DMUB service instances, while PSR-SU support is derived from the service object's firmware version.

Dependencies and integration points: used by `dmub_srv_hw_setup()` for `DMUB_ASIC_DCN314`, where `dmub->regs_dcn31` is set to `dmub_srv_dcn314_regs` and `is_psrsu_supported` is set to the local function. It depends on the DCN314 generated register headers matching the DCN31 common macro list.

Risks and test signals: risks include incorrect hard-coded segment bases, generated header field renames, and firmware-version policy becoming stale relative to DMUB firmware. Test signals are clean compile for DCN314, correct register offsets in register traces, PSR-SU disabled below 8.0.16 and enabled at or above it, and normal DCN31 reset/mailbox paths working with this table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.h

Purpose: declares the DCN314 register table and PSR-SU support predicate while reusing the DCN31 hardware interface.

Important APIs and control flow: exports `dmub_srv_dcn314_regs` as a `struct dmub_srv_dcn31_regs` instance and declares `dmub_dcn314_is_psrsu_supported()`. There is no inline logic; `dmub_srv.c` consumes these symbols during ASIC setup.

State and persistence behavior: the header introduces no state. It is a binding layer that lets DCN314 share all DCN31 callback implementations with a different register table and firmware capability gate.

Dependencies and integration points: includes `dmub_dcn31.h`, so all DMUB window/mailbox/GPINT types and function declarations remain aligned with DCN31. Integrated only through `dmub_srv_hw_setup()`.

Risks and test signals: risks are limited to declaration/definition mismatches and stale export use if DCN314 diverges from DCN31 behavior. Test signals are successful link of `dmub_srv.c` references and runtime PSR-SU query coverage on DCN314 platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c

Purpose: instantiates the DCN 3.1.5 DMUB register table. DCN315 largely reuses DCN31 hardware behavior but uses a local field list because GPINT interrupt fields are named `DMCUB_GPINT2_INT_EN` and `DMCUB_GPINT2_INT_ACK`.

Important APIs and control flow: `dmub_srv_dcn315_regs` expands common DCN31 register offsets plus `DMUB_DCN315_FIELDS()` for masks and shifts. The file has no runtime functions beyond the table initializer; all hardware operations are inherited from DCN31 through `dmub_srv_hw_setup()`.

State and persistence behavior: the exported const register table is immutable. Runtime DMUB state remains in the DMCUB hardware registers and in `struct dmub_srv` ring-buffer counters.

Dependencies and integration points: depends on `dcn_3_1_5_offset.h`, `dcn_3_1_5_sh_mask.h`, `dmub_reg.h`, and `dmub_dcn315.h`. `dmub_srv_hw_setup()` uses the table for `DMUB_ASIC_DCN315` while assigning the common DCN31 function set.

Risks and test signals: risks include a mismatch between the DCN315-specific interrupt field names and shared GPINT dataout code, register macro drift, and segment-base errors. Test signals include build coverage, GPINT dataout interrupt disable/ack/re-enable working on DCN315, and normal DCN31 reset/window/mailbox flows using the DCN315 offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.h

Purpose: defines the DCN315-specific DMUB field macro list and declares the DCN315 register table.

Important APIs and control flow: `DMUB_DCN315_FIELDS()` mirrors `DMUB_DCN31_FIELDS()` except for GPINT interrupt enable/ack field names, using `DMCUB_GPINT2_INT_EN` and `DMCUB_GPINT2_INT_ACK`. It exports `dmub_srv_dcn315_regs` as a DCN31-compatible register table.

State and persistence behavior: no direct state. The macro list controls which bit masks/shifts are loaded into the static register descriptor used by runtime register helpers.

Dependencies and integration points: includes `dmub_dcn31.h` and is consumed by `dmub_dcn315.c`. `dmub_srv.c` depends on the exported table when selecting DCN315.

Risks and test signals: risks include incomplete field parity with DCN31, field-name divergence across generated headers, and shared functions assuming fields not present in `DMUB_DCN315_FIELDS()`. Test signals are compile-time macro expansion and GPINT interrupt handling on DCN315 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c

Purpose: instantiates the DCN 3.1.6 DMUB register table by combining DCN31 common register/field macros with DCN316 generated offsets and masks.

Important APIs and control flow: `dmub_srv_dcn316_regs` expands `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN31_FIELDS()` using fixed DCN316 segment bases. There are no local hardware callbacks; DCN316 uses the common DCN31 vtable.

State and persistence behavior: no mutable state. The const table persists for the kernel lifetime and supplies register metadata to `dmub_reg.h` macros through `dmub->regs_dcn31`.

Dependencies and integration points: depends on `dcn_3_1_6_offset.h`, `dcn_3_1_6_sh_mask.h`, and the DCN31 common register definition. `dmub_srv_hw_setup()` selects the table for `DMUB_ASIC_DCN316`.

Risks and test signals: risks include generated-register drift, hard-coded segment bases not matching the IP block, and DCN316 later requiring behavior not covered by DCN31 callbacks. Test signals include successful DMUB boot, mailbox and GPINT operation, and diagnostic register reads on DCN316 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.h

Purpose: declares the DCN316 register table while reusing the DCN31 DMUB hardware interface.

Important APIs and control flow: exports `dmub_srv_dcn316_regs` as a `struct dmub_srv_dcn31_regs`. No functions are declared beyond the inherited DCN31 API.

State and persistence behavior: no state; this is a link-time declaration layer.

Dependencies and integration points: includes `dmub_dcn31.h`; used by `dmub_srv.c` to bind `DMUB_ASIC_DCN316`.

Risks and test signals: risks are declaration/definition mismatch and accidental omission from ASIC setup. Test signals are successful link and DCN316 service initialization selecting the expected register table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c

Purpose: implements the DCN 3.2 DMUB hardware callbacks used by the service core. It initializes dynamic register offsets from `dc_context`, resets and starts DMCUB, programs firmware windows, configures mailbox regions, handles GPINT, exposes boot status/options, captures diagnostics, supports DMUB-in-system-memory mode, and saves SubVP surface addresses in scratch registers.

Important APIs and control flow: `dmub_srv_dcn32_regs_init()` fills the mutable DCN32 offset/mask/shift table. `dmub_dcn32_reset()` sends `DMUB_GPINT__STOP_FW`, waits for scratch response and PWAIT status, asserts soft reset, disables DMCUB, disables region3 CW2-CW7 windows, resets mailbox pointers, clears scratch0, and clears GPINT. `reset_release()` releases MMHUBBUB reset, writes PSP version to scratch15, enables DMCUB/traceport, and drops soft reset. `backdoor_load()` translates framebuffer addresses through FB base/offset before programming CW0/CW1; ZFB mode uses raw offsets. `setup_windows()` maps CW3-CW6 and region5 but ignores CW2/region6. Mailbox helpers program base/size and read/write pointers. GPINT dataout handling disables interrupt delivery, clears dataout, toggles ack, then reenables interrupt. Diagnostics copy scratch0-16, fault addresses, mailbox state, enable/reset/PWAIT/trace/CW6 flags, and GPINT datain0.

State and persistence behavior: persistent hardware state includes DMCUB enable/reset, region window registers, scratch boot/status fields, mailbox pointers, and interrupt bits. Software state is updated indirectly through `struct dmub_srv`; `save_surf_addr()` uses scratch15 and scratch23 as rotating selectors for two SubVP indices and stores low plane/meta addresses into scratch9/11/12/13/18/19/20/22.

Dependencies and integration points: depends on `dmub_reg.h`, `dcn_3_2_0_offset.h`, `dcn_3_2_0_sh_mask.h`, `dc_types.h`, and `dc_hw_types.h`. `dmub_srv_hw_setup()` installs these callbacks for DCN32/DCN321 and uses them during `dmub_srv_hw_init()`, inbox0 helpers, wait paths, outbox trace reads, diagnostics, and SubVP support.

Risks and test signals: risks include timeout loops sharing one counter in reset, address translation underflow if FB base/offset is wrong, CW2/region6 ignored despite generic service passing them, mailbox pointer access without locking in stat paths, scratch-register ABI coupling, and only low address parts saved for SubVP. Test signals include DMUB stop/reset without debugger break, boot status `dal_fw`, valid inbox/outbox pointer movement, GPINT dataout interrupts acking once, diagnostics populated after timeout, system-memory TMR register set to `0x4`, and SubVP scratch toggling as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.h

Purpose: declares the DCN32 DMUB register inventory and callback surface. It extends DCN31 with region6, scratch16-23, GPINT datain0, DMCUB region3 TMR AXI-space selection, and dynamic register-table storage.

Important APIs and control flow: `DMUB_DCN32_REGS()` and `DMUB_DCN32_FIELDS()` generate offset/mask/shift structs for `struct dmub_srv_dcn32_regs`. Function declarations cover reset/release, normal/ZFB backdoor load, window setup, inbox1/outbox1/outbox0 mailbox helpers, support/init detection, GPINT, boot options, diagnostics, system-memory configuration, inbox0 command/ack helpers, SubVP surface save, and dynamic register initialization.

State and persistence behavior: no direct state, but the non-const register table is filled per device by `dmub_srv_dcn32_regs_init()` using `ctx->dcn_reg_offsets`. Runtime persistence lives in DMCUB registers and scratch fields.

Dependencies and integration points: includes `dmub_dcn31.h` for common DMUB types. `dmub_srv.c` owns the static `dmub_srv_dcn32_regs` storage and assigns this API for DCN32/DCN321.

Risks and test signals: risks include dynamic offset initialization being skipped, macro mismatch with generated DCN32 headers, and service callbacks assuming function declarations remain in sync with the implementation. Test signals include `init_reg_offsets` invocation before first MMIO access, compile coverage, and operational inbox0/inbox1/outbox/GPINT paths on DCN32 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c

Purpose: implements DCN 3.5 DMUB hardware callbacks. It follows the DCN32 model but adds DCN35 boot-option richness, clock-gate override programming, region6 setup, pre-OS firmware trace discovery, hardware-powered-up checks, and detection-required status.

Important APIs and control flow: `dmub_srv_dcn35_regs_init()` fills the DCN35 register table from runtime DCN offsets. `reset()` sends STOP_FW, waits for GPINT ack, stop response, and PWAIT, then forces reset/disable and clears mailbox pointers/scratch0. `reset_release()` writes PSP version, disables LONO display/SOC/DMCUB clock gating through `DMU_CLK_CNTL`, enables DMCUB/traceport, releases DMUIF reset, then releases DMCUB soft reset. `backdoor_load()` translates CW0/CW1 addresses using DCN VM FB registers, while ZFB uses raw offsets and sets memory unit id. `setup_windows()` maps CW3-CW6, region5, and region6. `enable_dmub_boot_options()` preserves pre-existing DPIA enable state and programs many feature bits: Z10, DPIA, USB4 CM version, HPD interrupt support, power optimization, clock DS/gate disables, IPS, SLDO, non-transparent setconfig, HBR3 SSC, DPIA bandwidth allocation, and boot CRC fields. `get_preos_fw_info()` recognizes VBIOS-loaded firmware from scratch1 bit 6 and reconstructs trace buffer physical address/size from CW5 registers.

State and persistence behavior: persistent state lives in DMCUB window/mailbox/scratch/interrupt registers. Software fields touched include `dmub->dpia_supported`, `dmub->debug`, `dmub->preos_info`, and power/init state managed by `dmub_srv.c`. FB base/offset currently ignores `soc_fb_info` because that code is commented out.

Dependencies and integration points: depends on DCN 3.5 generated offsets/masks, `dmub_reg.h`, `dc_types.h`, and DMUB command unions. `dmub_srv_hw_setup()` uses these callbacks for DCN35, and also for DCN351/DCN36 with different register-offset init functions.

Risks and test signals: risks include STOP_FW timeout still forcing reset without explicit status return, commented-out SoC FB override changing address translation behavior, boot option field drift with firmware, repeated scratch14 reads to preserve boot CRC bits, unchecked `region6`, and pre-OS trace calculation depending on CW5 layout. Test signals include DMCUB clock-gate disable bits set before boot, mailbox ready and powered-up status true, DPIA/USB4 feature negotiation visible in scratch14, pre-OS trace info populated only for VBIOS firmware, and region6 mappings visible in register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.h

Purpose: declares the DCN35 register layout and hardware API. It extends DCN32-style DMUB control with `DMU_CLK_CNTL` and LONO clock-gate-disable fields used during reset release.

Important APIs and control flow: `DMUB_DCN35_REGS()` includes DMCUB control, mailbox, region3/4/5/6, scratch0-21, GPINT, support, FB base/offset, fault, TMR AXI-space, interrupts, and `DMU_CLK_CNTL`. `DMUB_DCN35_FIELDS()` supplies masks/shifts for enable/reset, window top/enable fields, support, FB fields, GPINT interrupt, PWAIT, and the three LONO gate-disable bits. Declared callbacks cover all DCN32-like operations plus `get_fw_boot_option()`, `should_detect()`, `is_hw_powered_up()`, `get_preos_fw_info()`, and register-offset initialization.

State and persistence behavior: no local state; the mutable `struct dmub_srv_dcn35_regs` is filled per ASIC/revision. Runtime state persists in DMCUB registers and DMUB service fields.

Dependencies and integration points: includes `dmub_dcn31.h`; implemented by `dmub_dcn35.c` and reused by DCN351/DCN36 register initializers. `dmub_srv.c` binds this API for DCN35/DCN351/DCN36.

Risks and test signals: risks include field-list drift across DCN35, DCN351, and DCN36 generated headers, scratch count differences from DCN32, and register table initialization ordering. Test signals include compile coverage for all three revisions and boot/reset traces showing `DMU_CLK_CNTL` updates and working region6/pre-OS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c

Purpose: supplies the DCN 3.5.1 register-offset initializer for the otherwise shared DCN35 DMUB hardware implementation.

Important APIs and control flow: `dmub_srv_dcn351_regs_init()` fills `dmub->regs_dcn35` by expanding `DMUB_DCN35_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN35_FIELDS()` with `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`. It uses dynamic `ctx->dcn_reg_offsets` segment bases.

State and persistence behavior: no independent state. It mutates the service-owned DCN35 register descriptor during initialization.

Dependencies and integration points: depends on `dmub_dcn351.h`, `dmub_reg.h`, and DCN351 generated headers. `dmub_srv_hw_setup()` selects this init function for `DMUB_ASIC_DCN351` while using the DCN35 callback set.

Risks and test signals: risks include missing fields in DCN351 generated headers and use before `init_reg_offsets` runs. Test signals include successful DCN351 build, initialized offsets differing from DCN35 where expected, and normal DCN35 boot/mailbox/pre-OS behavior on DCN351.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.h

Purpose: declares the DCN351 register initialization hook and reuses the DCN35 DMUB API.

Important APIs and control flow: exports `dmub_srv_dcn351_regs_init(struct dmub_srv *dmub, struct dc_context *ctx)`. No other behavior is declared.

State and persistence behavior: no state; it identifies the per-revision initializer used to populate service-owned register metadata.

Dependencies and integration points: includes `dmub_dcn35.h`; selected by `dmub_srv_hw_setup()` for DCN351.

Risks and test signals: risks are declaration drift and omission from ASIC setup. Test signals are clean link and `init_reg_offsets` dispatch for DCN351.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c

Purpose: supplies the DCN 3.6 register-offset initializer for the shared DCN35 DMUB hardware implementation.

Important APIs and control flow: `dmub_srv_dcn36_regs_init()` fills `dmub->regs_dcn35` from `DMUB_DCN35_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN35_FIELDS()` using `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.

State and persistence behavior: no independent state. It mutates the service-owned DCN35 register metadata table before callbacks use `REG_*` macros.

Dependencies and integration points: depends on `dmub_dcn36.h`, `dmub_reg.h`, and DCN360 generated headers. `dmub_srv_hw_setup()` selects this initializer for `DMUB_ASIC_DCN36`.

Risks and test signals: risks include generated field mismatch and DCN36 behavioral divergence not represented by DCN35 callbacks. Test signals include compile/link success, correct offset initialization, DMUB boot and region/window/mailbox operation on DCN36, and powered-up predicate matching firmware status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.h

Purpose: declares the DCN36 register initialization hook while inheriting the DCN35 DMUB API.

Important APIs and control flow: exports `dmub_srv_dcn36_regs_init()`. The function is called by the service core during register-offset setup for DCN36.

State and persistence behavior: no state; it only exposes an initializer for service-owned register metadata.

Dependencies and integration points: includes `dmub_dcn35.h`; used by `dmub_srv.c` for `DMUB_ASIC_DCN36`.

Risks and test signals: risks are declaration drift and missed dispatch. Test signals include build/link coverage and observed `init_reg_offsets` call on DCN36.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c

Purpose: implements DCN 4.0.1 DMUB hardware callbacks. It resembles DCN32 for reset/window/mailbox/GPINT paths and adds a register-mailbox command/response interface with host interrupt control and DMCUB register outbox support.

Important APIs and control flow: `dmub_srv_dcn401_regs` is a const register table using DCN 4.1 generated offsets/masks and a fixed segment2 base. Reset sends STOP_FW, waits for scratch response and PWAIT, asserts soft reset, disables DMCUB and region windows, clears mailbox pointers and scratch0, and clears GPINT. Backdoor load supports translated and ZFB CW0/CW1 programming. Window setup maps CW3-CW6 plus region5/region6. Boot options program Z10 disable and `skip_phy_access`. Diagnostic capture additionally records secure reset status and CW0 enable state. `send_reg_inbox0_cmd_msg()` writes up to 15 payload dwords from a 64-byte `union dmub_rb_cmd` into `DMCUB_REG_INBOX0_MSG0..14`, then writes the header dword to `DMCUB_REG_INBOX0_RDY` to trigger DMUB. Response helpers read the response/header and message dwords, toggle/enable host inbox0 response interrupts, ack outbox0 ready interrupts, read outbox0 message0, write outbox0 response, and report interrupt status.

State and persistence behavior: persistent hardware state includes regular mailbox pointers, GPINT/scratch fields, register-mailbox message registers, and `HOST_INTERRUPT_CSR` bits. Software state for submitted/reported register commands is maintained by `dmub_srv.c`, not this file.

Dependencies and integration points: depends on `dmub_dcn401.h`, `dmub_reg.h`, `dcn_4_1_0_offset.h`, and `dcn_4_1_0_sh_mask.h`. `dmub_srv_hw_setup()` installs these callbacks for `DMUB_ASIC_DCN401` and still defaults the inbox type to framebuffer unless overridden.

Risks and test signals: risks include fixed segment coverage only defining segment2, manual switch statements for each payload register, payload-size interpretation excluding dword0, interrupt ack polarity/timing, defaulting to FB despite register-mailbox support, and reset timeout debugger break. Test signals include 64-byte command static assertion, register-inbox commands producing response interrupts, outbox0 ready interrupts acking, fallback FB command path still working, and diagnostics showing secure reset/CW0 state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.h

Purpose: declares the DCN401 DMUB register inventory and hardware API, including register-mailbox registers and host interrupt fields absent from older DCN31/32/35 headers.

Important APIs and control flow: `DMUB_DCN401_REGS()` includes DMCUB control, mailboxes, region windows, scratch0-17, GPINT, support/reset/FB/timer/fault/TMR registers, interrupt enable/ack/status, `DMCUB_REG_INBOX0_RDY`, `DMCUB_REG_INBOX0_MSG0..14`, `DMCUB_REG_INBOX0_RSP`, `DMCUB_REG_OUTBOX0_RDY`, `DMCUB_REG_OUTBOX0_MSG0`, `DMCUB_REG_OUTBOX0_RSP`, and `HOST_INTERRUPT_CSR`. `DMUB_DCN401_FIELDS()` includes normal DMUB fields plus register inbox/outbox interrupt status, ack, and enable fields. Function declarations cover both legacy framebuffer mailbox callbacks and the register inbox/outbox helpers.

State and persistence behavior: no state in the header. The const `dmub_srv_dcn401_regs` table maps the declared fields to runtime MMIO accesses.

Dependencies and integration points: includes `dmub_dcn31.h`; implemented by `dmub_dcn401.c` and bound by `dmub_srv.c` for `DMUB_ASIC_DCN401`.

Risks and test signals: risks include field-list drift with DCN 4.1 generated headers, missing register-mailbox callbacks if `dmub_srv_hw_funcs` changes, and interrupt field polarity mismatches. Test signals include compile coverage and command/response traffic through both FB and register inbox paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c

Purpose: implements DCN 4.2 DMUB hardware callbacks. It combines DCN35-style boot/reset/window behavior with DCN401-style register inbox/outbox operations and dynamic register-offset initialization.

Important APIs and control flow: `dmub_srv_dcn42_regs_init()` fills the DCN42 register table from `ctx->dcn_reg_offsets`. Boot options program DPIA/USB4/power/clock/IPS/SLDO/non-transparent/HBR3/PHY-access/DPIA-bandwidth fields. Reset follows the DCN35 pattern: STOP_FW, wait for ack/response/PWAIT, assert reset, disable DMCUB, clear mailbox pointers/scratch0, clear GPINT. Reset release writes PSP version, disables LONO clock gating, enables DMCUB/traceport, releases DMUIF and soft reset. Backdoor load, ZFB load, windows, mailboxes, GPINT, powered-up status, detection status, pre-OS trace discovery, diagnostics, inbox0 ack, and TMR system-memory configuration match DCN35 with DCN42 registers. Register-inbox functions match DCN401: payload dwords go to `DMCUB_REG_INBOX0_MSG0..14`, header goes to RDY, response reads RSP plus MSG0..14, and host interrupt bits are used for inbox0 response and outbox0 ready.

State and persistence behavior: persistent hardware state lives in DMCUB windows, mailboxes, scratch registers, interrupt fields, and register-mailbox registers. Software state is in `dmub_srv.c`; this file mutates `dmub->dpia_supported`, `debug`, and `preos_info` through callbacks.

Dependencies and integration points: depends on `dmub_dcn35.h`, `dmub_dcn401.h`, `dmub_dcn42.h`, `dmub_reg.h`, and DCN 4.2 generated offset/mask headers. `dmub_srv_hw_setup()` binds it for `DMUB_ASIC_DCN42`, installs register-mailbox callbacks, enables register interrupts during hardware init, and still defaults the inbox type to framebuffer.

Risks and test signals: risks include duplicated DCN35/DCN401 logic drifting, `is_supported()` unconditionally returning true, commented-out SoC FB override, register-inbox payload loop/manual switch maintenance, duplicate assignment of `enable_reg_inbox0_rsp_int` in service setup, and boot option fields requiring firmware ABI parity. Test signals include DCN42 register offsets initialized before access, unconditional support accepted by callers, successful DMUB boot/powered-up status, working pre-OS trace recovery, register inbox response interrupts, outbox0 ready/response handling, and FB command fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.h

Purpose: declares the DCN42 DMUB register inventory and API. It merges DCN35 fields such as `DMU_CLK_CNTL` with DCN401 register-mailbox and `HOST_INTERRUPT_CSR` fields, while dropping `CC_DC_PIPE_DIS` support probing from the register list.

Important APIs and control flow: `DMUB_DCN42_REGS()` covers DMCUB control, mailboxes, region3/4/5/6, scratch0-21, GPINT, MMHUBBUB reset, FB base/offset, timer/fault/TMR, interrupts, clock control, register inbox/outbox message/response registers, and host interrupt CSR. `DMUB_DCN42_FIELDS()` provides masks/shifts for window enables, reset/control, FB/TMR, GPINT interrupt, PWAIT, LONO gates, and register inbox/outbox interrupt bits. Declarations are grouped by initialization, reset, firmware loading, mailbox, register mailbox, GPINT, status, boot status/options, timing, diagnostics, and pre-OS info.

State and persistence behavior: no direct state; `struct dmub_srv_dcn42_regs` is mutable and initialized per device. Runtime values persist in DMCUB registers and service-owned state.

Dependencies and integration points: includes `dmub_dcn35.h` and `dmub_dcn401.h`; implemented by `dmub_dcn42.c` and assigned by `dmub_srv_hw_setup()` for DCN42.

Risks and test signals: risks include a large macro surface drifting from generated DCN42 headers, duplicated declaration groups diverging from implementation, and unconditional support behavior needing service-layer awareness. Test signals are clean compile, initialized offsets/masks, working clock-gate release, and register-mailbox interrupt coverage on DCN42 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.c

Purpose: implements generic DMUB register field set/update/get helpers used by all ASIC-specific DMUB hardware files.

Important APIs and control flow: `set_reg_field_value_masks()` composes a masked field value into an accumulator. `set_reg_field_values()` consumes the first field and remaining varargs triples of shift, mask, and value to build one combined value/mask pair. `dmub_reg_update()` reads the current register through `srv->funcs.reg_read`, applies the combined mask/value, and writes it back. `dmub_reg_set()` applies fields to an explicit initial register value and writes without a read. `dmub_reg_get()` reads a register and extracts one masked field.

State and persistence behavior: no persistent software state. It writes hardware registers through the service's host callbacks. Register updates are read-modify-write operations, so persistence depends on hardware accepting the write and no concurrent writer changing the same register between read and write.

Dependencies and integration points: depends on `dmub_reg.h`, `dmub_srv.h`, C varargs, `ASSERT`, and `struct dmub_srv_funcs` register callbacks. All `REG_SET_*`, `REG_UPDATE_*`, and `REG_GET` macro uses in DCN files flow through these helpers.

Risks and test signals: risks include unchecked `reg_read`/`reg_write` failures because callbacks have no status channel, read-modify-write races on shared registers, varargs type/order mistakes, truncating shifts to `uint8_t`, and no validation that field values fit their masks. Test signals include unit-style field packing/extraction checks, register traces showing unrelated bits preserved, and stress coverage where interrupt ack/update paths share registers with firmware or other host code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h

Purpose: defines the macro layer that maps per-ASIC register tables to DMUB MMIO read/write, field set/update, and field get operations.

Important APIs and control flow: `BASE`, `REG_OFFSET`, `FD_SHIFT`, and `FD_MASK` bridge generated register names to offsets and bit metadata. `REG`, `FD`, and `FN` look up offsets/shifts/masks in the active `REGS` table, while `REG_READ` and `REG_WRITE` call the host callbacks through `CTX`. `REG_SET`, `REG_SET_2`, `REG_SET_3`, and `REG_SET_4` call `dmub_reg_set()` with an initial value. `REG_UPDATE`, `REG_UPDATE_2`, `REG_UPDATE_3`, and `REG_UPDATE_4` call `dmub_reg_update()` for read-modify-write. `REG_GET` extracts a field through `dmub_reg_get()`.

State and persistence behavior: no state, but the macros depend on each `.c` file defining `BASE_INNER`, `CTX`, and `REGS` correctly. Runtime persistence is hardware register state.

Dependencies and integration points: includes `dmub_cmd.h` for command types and declares the three helper functions implemented in `dmub_reg.c`. Every DMUB ASIC file includes this header after setting up its register table model.

Risks and test signals: risks include macro context leakage if `CTX`/`REGS` are wrong, field names not present in the table, no status propagation from MMIO callbacks, and multi-field vararg misuse only detected at runtime. Test signals are compile-time expansion across all ASIC files, boot register traces matching generated offsets, and read-modify-write preserving adjacent fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c

Purpose: implements the DMUB service core: firmware metadata extraction, ASIC-specific hardware function binding, memory-region sizing, framebuffer/GART address assignment, hardware initialization/reset, command queueing/execution, wait/sync helpers, GPINT wrappers, diagnostics, outbox trace reads, inbox0/register-inbox command support, and power-state tracking.

Important APIs and control flow: metadata helpers locate `DMUB_FW_META_MAGIC` in legacy BSS or combined inst/const blobs and try custom, 256-byte, and 512-byte PSP footer sizes. `dmub_srv_hw_setup()` switches on `enum dmub_asic`, installs the correct register table and hardware callbacks for DCN20 through DCN42, selects revision-specific register initializers, and chooses a default inbox interface. `dmub_srv_create()` zeroes the service, stores callbacks/context/ASIC/firmware/inbox settings, calls hardware setup, applies optional callback overrides, validates required inbox callbacks, and marks `sw_init`. Region helpers align window sizes and compute separate FB/GART allocation totals. `dmub_srv_hw_init()` validates all windows, copies SoC FB/PSP info, resets hardware, creates CW0-CW6 and region6 mappings, flushes instruction memory if CPU-loaded, backdoor-loads firmware, programs mailboxes/outboxes, enables register interrupts, initializes inbox1/outbox1/outbox0 ring buffers, writes boot options, optionally skips panel power sequence, releases reset, and marks `hw_init`/D0. Command APIs push FB commands to the inbox1 ring and flush pending data before updating HW write pointer; register commands clear previous ack, write register inbox payload/header, and update submitted/pending counters. Wait/sync APIs poll mailbox pointers and register response interrupt status, track submitted versus reported counts, and return timeout/hardware-failure statuses.

State and persistence behavior: `struct dmub_srv` is the central mutable state: software/hardware init flags, firmware version/meta, hardware function table, register-table pointers, ring-buffer pointers/counters, last inbox write pointer, register-inbox pending/multi-pending state, power state, debug/pre-OS data, scratch/IB/cursor buffers, shared state, and SoC FB/PSP data. Hardware state is set by callbacks and persists until reset; service reset clears software mailbox counters to match hardware.

Dependencies and integration points: depends only on DMUB-local headers plus OS types. It integrates with display manager code through the public DMUB service API, caller-provided register read/write and delay/memory callbacks, `dmub_rb` ring helpers, DMUB command unions, firmware metadata, and DCN-specific callback implementations.

Risks and test signals: risks include very large ASIC switch tables drifting when callbacks are added, defaulting DCN401/DCN42 register-capable hardware to FB inbox, static global register tables shared across service instances, command waits mixing hardware emptiness with reported/submitted counters, FB/GART window alignment assumptions, CPU cache flush by readback only, unguarded trace/outbox callback assumptions, and service state reset wiping caller-visible data. Test signals include create failure on unsupported ASIC, correct region sizes/alignments, successful HW init through reset release, mailbox ready waits, FB queue full and pointer wrap tests, register inbox response interrupt tests, D3 command rejection, timeout diagnostics, pre-OS info retrieval, and sync after reset/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv_stat.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv_stat.c

Purpose: implements the lockless DMUB service stat/notification path for outbox1 messages. It extracts notifications generated by DMUB without taking DAL or DC locks.

Important APIs and control flow: `dmub_srv_stat_get_notification()` validates `hw_init`, reads the DMUB-updated outbox1 write pointer, pops the next `union dmub_rb_out_cmd` from `dmub->outbox1_rb`, translates command types into `struct dmub_notification`, advances the outbox ring, writes the hardware read pointer, and sets `pending_notification` based on whether more entries remain. Recognized messages include DP AUX reply, DP HPD/HPD IRQ, set-config reply, DPIA notification, HPD sense notify, and fused I/O.

State and persistence behavior: only `dmub->outbox1_rb` is modified by design, because the function is called locklessly. Hardware persistence is the outbox1 write/read pointer pair; the function updates read pointer after consuming one message.

Dependencies and integration points: depends on `dmub_srv_stat.h`, `dmub_cmd.h`, ring-buffer helpers, `dmub->hw_funcs.get_outbox1_wptr`, and `set_outbox1_rptr`. It is used by display notification handling code that cannot hold normal DMUB locks.

Risks and test signals: risks include assuming exclusive access to `outbox1_rb`, missing new outbox command types mapping to `NO_DATA`, absent callback validation, malformed DMUB messages causing partially initialized notifications, and pointer corruption if hardware writes invalid values. Test signals include AUX/HPD/set-config/DPIA/fused notifications delivered with correct instance/result fields, pending flag behavior with multiple messages, no mutation outside `outbox1_rb`, and safe invalid status when hardware is not initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/audio_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/audio_types.h

Purpose: defines shared AMD display audio data structures used for HDMI/DP audio programming, DTO calculation, and stream/audio capability propagation.

Important APIs and control flow: key types include `audio_dp_link_info` for link bandwidth, encoding, rate, lane count, and MST; `audio_crtc_info` for timing, pixel clock, DSC, color depth/encoding, refresh, repetition, and interlace; `azalia_clock_info` for DTO register values; `audio_dto_source`; `audio_pll_info` for source clock and spread-spectrum data; `audio_channel_associate_info` bitfield mapping eight logical channels; `audio_output` combining engine/signal/video/link/PLL data; and `audio_payload` with channel split mapping change.

State and persistence behavior: no runtime state. These structures are copied between display pipeline, audio, and link code; persistent meaning is in the ABI of field units such as 100 Hz, 10 kHz, kHz, and channel nibbles.

Dependencies and integration points: depends on `signal_types.h`, `fixed31_32.h`, and `dc_dp_types.h`. It integrates with audio packet/DTO programming, DP link configuration, and CRTC timing code.

Risks and test signals: risks include unit confusion across pixel-clock fields, bitfield layout assumptions in `audio_channel_associate_info`, display-name size limits, and keeping DP link encoding/rate enums synchronized. Test signals include audio DTO values matching expected sample clocks, HDMI/DP audio working for deep color/DSC/MST, and channel mapping changes producing correct payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/audio_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/bios_parser_interface.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/bios_parser_interface.h

Purpose: declares the public construction/destruction interface for the AMD display BIOS parser.

Important APIs and control flow: `struct bp_init_data` supplies `dc_context` and raw BIOS pointer. `dal_bios_parser_create()` returns a `struct dc_bios *` for a requested `enum dce_version`, and `dal_bios_parser_destroy()` tears it down through a pointer-to-pointer.

State and persistence behavior: no state in the header; created parser objects encapsulate BIOS parsing state elsewhere. The raw BIOS pointer must remain valid for the parser implementation's expected lifetime.

Dependencies and integration points: includes `dc_bios_types.h` and forward-declares `bios_parser`. Display core uses this interface to acquire VBIOS services for transmitter, clock, connector, and spread-spectrum tables.

Risks and test signals: risks include invalid BIOS pointers, wrong DCE/DCN version selection, lifecycle misuse of pointer-to-pointer destroy, and parser implementation drift from declared API. Test signals include successful parser creation for supported ASIC versions, graceful failure on bad BIOS tables, and no use-after-destroy under display teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/bios_parser_interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/bios_parser_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/bios_parser_types.h

Purpose: defines AMD display BIOS parser command/result enums and parameter structures for encoder, transmitter, CRTC timing, pixel clock, spread spectrum, connector capability, and bandwidth/latency data.

Important APIs and control flow: enums cover ATOM-style signal types, BIOS parser results, encoder/transmitter/external encoder actions, pipe and LVTMA actions, and DCE clock type. Structures include `bp_encoder_control`, `bp_external_encoder_control`, `bp_crtc_source_select`, `bp_transmitter_control`, load detection, hardware CRTC timing with polarity/interlace flags, pixel clock adjustment/programming parameters, DCE clock programming, spread-spectrum parameters, connector caps, encoder caps, SOC bounding-box latencies, and connector speed caps.

State and persistence behavior: no runtime state. These types are ABI-like contracts passed between display manager and BIOS parser/ATOM execution code; fields often carry firmware-specific units such as kHz, 100 Hz, 10 kHz, 100 ns, lane settings, and packed bit capability flags.

Dependencies and integration points: depends on `dm_services.h`, signal/object/GPIO/link service types, and display enums such as engine, transmitter, lane count, color depth, HPD, clock source, and graphics object IDs. BIOS parser implementations fill or consume these structures to drive VBIOS tables.

Risks and test signals: risks include typos preserved in enum names for compatibility, bitfield packing assumptions, direct VBIOS translation values that must not be renumbered, unit mismatches, missing fields for newer PHY/HPO/USB-C capabilities, and unsupported BIOS table versions. Test signals include BIOS table execution for encoder enable/setup, transmitter power and lane settings, pixel clock programming including YUV420/deep color/PHY-only flags, spread-spectrum values, and parsed DP/HDMI/UHBR capability bits matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/bios_parser_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dal_asic_id.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dal_asic_id.h

Purpose: centralizes AMD display ASIC family, revision, and device ID constants plus revision-classification macros used across the display driver.

Important APIs and control flow: defines internal revision IDs and predicates for SI, CI, KV/Kabini/Bhavani/Godavari, VI/Polaris/Vegam, CZ/Stoney, AI/Vega, Raven/Raven2/Picasso/Renoir, Navi/Green Sardine, Vangogh, Yellow Carp, GC 10.3.x, GC 11.x, DCN36, GC 12/DCN4/DCN401, and selected device IDs. It also defines family IDs such as `FAMILY_SI`, `FAMILY_NV`, `FAMILY_YELLOW_CARP`, and `AMDGPU_FAMILY_GC_*`.

State and persistence behavior: no runtime state. These macros are compile-time classification logic over chip revision/device/family values discovered elsewhere.

Dependencies and integration points: standalone header used by display capability, resource, and ASIC-specific initialization code to select DCN/DCE paths, workarounds, and feature gates.

Risks and test signals: risks include overlapping revision ranges, duplicated constants such as `AI_UNKNOWN`, macros without parentheses around all arguments in older patterns, stale device IDs, and new ASIC revisions falling into broad predicates unintentionally. Test signals include ASIC detection unit checks over boundary revision values, correct resource selection for DCN36/DCN4/DCN401, and boot logs identifying expected family/revision for supported GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dal_asic_id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dal_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dal_types.h

Purpose: declares common DAL forward types and the display engine/DCN version enumeration.

Important APIs and control flow: forward-declares `dal_logger` and `dc_bios`. `enum dce_version` lists DCE 6.0 through 12.1, then DCN 1.0 through 4.2, with separate `DCE_VERSION_MAX` and `DCN_VERSION_MAX` markers.

State and persistence behavior: no state. The enum values are used as selectors for BIOS parser creation, resource construction, and version-gated display behavior.

Dependencies and integration points: includes `signal_types.h`; consumed by display core, BIOS parser, and ASIC resource code.

Risks and test signals: risks include enum ordering assumptions, max marker placement, new DCN versions needing coordinated additions, and mixed DCE/DCN comparisons. Test signals include version switch coverage for DCN 3.14/3.15/3.16/3.5/3.51/3.6/4.01/4.2 and BIOS parser/resource selection using the expected version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dal_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/ddc_service_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/ddc_service_types.h

Purpose: defines DDC/AUX service result and capability types plus DisplayPort branch/device IDs and PSR-related DPCD offsets used by AMD display link detection.

Important APIs and control flow: constants identify known DP branch/dongle device IDs, branch revisions, forced PSR-SU capability offset, and PSR active-vtotal registers. `enum ddc_result` reports DDC transaction outcomes, including busy, timeout, protocol/NACK, incomplete, invalid operation, overflow, and HPD disconnect. `enum ddc_service_type` distinguishes connector and MST service instances. `display_sink_capability` captures dongle type, downstream sink count validity, audio/video latencies, HDMI pixel/deep-color caps, spread-spectrum support, DP lane/rate/spread fields, DP-HDMI 3D conversion, eDP sink cap validity, transaction type, and signal. `av_sync_data` stores latency bytes read from DPCD.

State and persistence behavior: no direct state. These structures persist as cached sink capability data in link/DDC objects elsewhere.

Dependencies and integration points: relies on display enums for dongle, color depth, DDC transaction, and signal types. Integrated with I2C-over-AUX/DDC probing, MST branch handling, dongle capability parsing, PSR-SU forcing, and AV sync handling.

Risks and test signals: risks include typo-preserved result names, stale vendor/device IDs, unit mismatch for latency fields, misspelled `dp_link_spead`, and capability caches becoming invalid across hotplug. Test signals include DDC failure mapping, known dongle detection, MST downstream count handling, eDP cap caching, PSR active-vtotal register access, and AV sync values parsed from DPCD bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/ddc_service_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dpcd_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dpcd_defs.h

Purpose: supplies AMD display-local DPCD constants and enums not yet available, or historically duplicated, from DRM DP helper headers. It covers panel replay, PSR, link/audio test patterns, source-specific DPCD locations, and LTTPR count.

Important APIs and control flow: guarded `#ifndef` defines add panel replay capability/configuration/granularity/error/status bits, sink hardware revision, and `DP_TOTAL_LTTPR_CNT` when missing upstream. Enums define DPCD revisions, downstream port types, link test patterns, test color formats/bit depths/dynamic range, PHY test patterns including 128b/132b and PRBS variants, audio test pattern/rate/channel/period values, training pattern encodings including TPS4 and 128b/132b CDS, and PSR sink states. Source/sink DPCD offsets cover source sequence/table/payload/sink cap, backlight, DRR granularity, minimum hblank, panel replay status/deviation/emission/frame skip.

State and persistence behavior: no state. Constants are used as protocol register addresses and values in AUX transactions; compatibility depends on matching the DisplayPort/eDP specifications and DRM helper definitions.

Dependencies and integration points: includes `<drm/display/drm_dp_helper.h>` and supplements it conditionally. Used by link training, compliance test, audio test, PSR, Panel Replay, backlight, LTTPR, and AUX read/write code.

Risks and test signals: risks include local definitions diverging from upstream DRM helpers, enum values needing exact DPCD encodings, new helper definitions changing conditional coverage, and protocol code assuming unsupported sink features. Test signals include compile without redefinition warnings across kernel versions, DP/eDP compliance tests selecting correct patterns, PSR/Panel Replay AUX transactions to expected offsets, audio test pattern handling, and LTTPR count reads at `0xF000A`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dpcd_defs.h -->

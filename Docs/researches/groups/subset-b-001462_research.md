# Research: subset-b-001462

This grouped report covers the DMUB command ABI and early DCN hardware support files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/`. Each section is source-tree-aligned and intended to be split into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/inc/dmub_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/inc/dmub_cmd.h

## Purpose

`dmub_cmd.h` is the host/firmware ABI contract for AMD Display Microcontroller Unit B (DMCUB/DMUB). It defines the packed command records, outbox notifications, scratch-register status layouts, GPINT command format, feature capability structures, shared-state blocks, trace entry layout, and inline ringbuffer helpers used by the display driver and DMUB firmware. The file is not executable firmware logic; its main job is binary layout stability between the Linux driver, VBIOS-facing command helpers, and DMUB firmware parsers.

The header includes Linux integer/string/delay support and `atomfirmware.h`, then deliberately wraps command payloads in `#pragma pack(push, 1)` to keep the 64-byte ringbuffer command ABI byte-exact. Many comments explicitly say command IDs are stable and must not be reused or modified, making this file a compatibility boundary.

## Important APIs, Types, And Constants

Key global sizing and limits include `DMUB_RB_CMD_SIZE` at 64 bytes, `DMUB_RB_MAX_ENTRY` at 128, `DMUB_RB_SIZE`, `DMUB_REG_INBOX0_RB_MAX_ENTRY`, stream and plane caps (`DMUB_MAX_STREAMS`, `DMUB_MAX_PLANES`, `DMUB_MAX_PHANTOM_PLANES`), dirty rect count, ABM curve/histogram sizes, and command-version constants for PSR, dirty rects, cursor updates, and ABM.

Addressing and platform-neutral helpers are provided by `union dmub_addr`, `PHYSICAL_ADDRESS_LOC`, `dmub_memcpy`, `dmub_memset`, `dmub_memcmp`, and `dmub_udelay`. These allow the same ABI header to be used across host and firmware-style environments.

Firmware metadata is described by `union dmub_fw_meta_feature_bits`, `struct dmub_fw_meta_info`, and `union dmub_fw_meta`. The metadata includes a magic value, firmware and trace-buffer region sizes, firmware version, DAL firmware flag, shared-state size/count, and static feature bits such as shared-state link detection, cursor offload support, and inbox0 lock support.

Status and boot signaling use scratch-register layouts: `union dmub_fw_boot_status`, `enum dmub_fw_boot_status_bit`, `union dmub_lvtma_status`, and `union dmub_fw_boot_options`. Boot options include environment flags, optimized init, PHY-skip flags, DPIA/USB4 options, power optimization, IPS disable controls, clock deep-sleep controls, HBR3 overrides, DPIA bandwidth allocation disabling, and boot-time CRC controls.

The GPINT path is defined by `union dmub_gpint_data_register` and `enum dmub_gpint_command`. GPINT commands cover firmware version query, STOP_FW, PSR and Replay state/residency, detection completion, bounding-box copy/address programming, trace-buffer mask reads/writes, IPS residency/histogram queries, debug setup, IPS wake, and panel power-off sequencing.

The main inbox command taxonomy is `enum dmub_cmd_type`. It includes register-sequence offload, query-feature-caps, PSR, MALL, ABM, dirty rects, cursor info, HW lock, DP AUX, outbox enable, idle optimization, clock manager, panel control, CAB, firmware-assisted MCLK switch/FAMS, DPIA, EDID CEA, USB-C cable ID, HPD query, Replay, secure display, PSP, fused IO, LSDMA, IPS, cursor offload, smart power OLED, Panel Replay, IHC, boot-time CRC, and VBIOS shared commands. Outbox notifications are defined by `enum dmub_out_cmd_type`.

Core command framing is `struct dmub_cmd_header`, an 8-bit type, 8-bit subtype, return/multi-command/register-based flags, and a 6-bit payload length excluding the header. `union dmub_rb_cmd` overlays every inbox command on a 64-byte entry; `union dmub_rb_out_cmd` overlays every outbox notification.

Major payload families include:

- Register offload: read-modify-write, field update sequences, burst writes, and register waits.
- Display transport and VBIOS: DIG encoder, DIG transmitter, pixel clock, display power gating, LVTMA, PHY FSM, DP alt query, DP AUX, HPD, DPIA SET_CONFIG/MST/TPS/HPD interrupt, EDID CEA parsing, and USB-C cable ID.
- Power/display optimization: MALL, CAB, idle optimization, clock notifications, firmware-assisted MCLK switch, FAMS2, FAMS2 indirect buffers, FAMS2 DRR update, and FAMS2 flip.
- Panel self-refresh and replay: PSR command payloads, dirty rect/cursor update payloads, Replay copy/enable/power/timing/coasting commands, Panel Replay copy/enable/update/general commands, and related debug/runtime flags.
- Backlight and panel control: ABM config tables, ABM set pipe/backlight/level/ambient/PWM/pause/save-restore/query/ACE/histogram/event commands, panel control payloads, and smart power OLED payloads.
- Security and diagnostics: secure display ROI commands, PSP ASSR, IHC HDCP interrupt routing, IPS residency command/output structures, cursor offload shared state and commands, boot-time CRC, trace entry definitions, and fused I/O request descriptors.

Ringbuffer helpers include `dmub_rb_empty`, `dmub_rb_num_outstanding`, `dmub_rb_num_free`, `dmub_rb_full`, `dmub_rb_push_front`, `dmub_rb_out_push_front`, `dmub_rb_front`, `dmub_rb_get_rptr_with_offset`, `dmub_rb_peek_offset`, `dmub_rb_out_front`, `dmub_rb_pop_front`, `dmub_rb_flush_pending`, `dmub_rb_init`, and `dmub_rb_get_return_data`.

## Control Flow And Data Flow

The command flow is producer/consumer based. Driver code fills a `union dmub_rb_cmd`, sets `header.type`, `header.sub_type`, and `header.payload_bytes`, pushes it into an inbox ring with `dmub_rb_push_front`, flushes pending memory reads if needed, and advances a hardware mailbox write pointer through generation-specific DMUB hardware functions. Firmware consumes the 64-byte command, may write return data into the same entry for commands with return status, and advances the read pointer. Outbox flow is symmetric: firmware writes a `union dmub_rb_out_cmd`, driver copies it with `dmub_rb_out_front`, then advances the outbox read pointer.

GPINT flow is separate from framebuffer mailbox flow. The driver formats a 32-bit `dmub_gpint_data_register`, writes it to a GPINT data-in register through hardware functions, and waits for firmware to clear the status field and optionally publish a response in scratch registers or data-out registers.

Shared state is another communication path used where inbox/outbox availability is limited. The shared-state region is fixed in 256-byte feature blocks with an 8-byte feature header and 248-byte payload. IPS firmware/driver signals, debug setup, and cursor offload state use this region.

Indirect buffers extend the 64-byte command limit. ABM initialization, FAMS2 IB config, IPS query results, ACE/histogram dumps, cursor offload state, and boot-time CRC use GPU addresses plus sizes to point firmware at larger host-visible buffers.

## State And Persistence Behavior

The file defines persistent ABI state rather than owning runtime storage. Persistent or cross-call state includes scratch register interpretation, firmware metadata at a fixed image offset, shared-state feature blocks, ringbuffer read/write pointers, command return data stored in the previous ring entry, ABM save/restore payloads, IPS residency accumulators, trace buffers, and cursor offload write indices.

Ringbuffer state is transient but safety-critical. One entry is intentionally left unusable to distinguish full from empty states. Pointer arithmetic wraps by capacity and assumes capacity is valid and aligned to `DMUB_RB_CMD_SIZE`.

Many payloads have explicit padding and version fields. These are state-persistence safeguards: the firmware can evolve behavior while old command layouts remain decodable.

## Dependencies And Integration Points

This header is consumed by `dmub_srv.h`, DMUB generation hardware files, display core services (`dc_dmub_srv.c`), BIOS command translation, PSR/Replay/ABM helpers, panel control, link encoder code, HPD/AUX/DPIA paths, and outbox notification code. It also depends on `atomfirmware.h` for ATOM/VBIOS payload structures embedded in DMUB commands.

Generation files such as `dmub_dcn20.c`, `dmub_dcn30.c`, and `dmub_dcn31.c` use the GPINT, boot status/options, address, and ringbuffer command definitions. Service code sets command payload sizes using `sizeof(struct dmub_cmd_...)`, so struct size drift directly affects the command ABI.

## Risks And Edge Cases

The highest risk is ABI drift. Command IDs, enum values, field order, packing, and explicit padding must stay synchronized with firmware. A single oversized payload can silently exceed the 60-byte payload limit unless compile-time checks catch it in the relevant path.

Bitfield layout is compiler-sensitive in general, but this driver and firmware contract appears designed for the same expected C ABI. Changes to bitfield widths or enum storage assumptions could break command parsing.

Ringbuffer helpers do not validate that capacity is a multiple of 64, that pointers are in range, or that the caller serialized producer/consumer access. Those checks are expected at a higher layer or by construction.

Some inline copying uses byte loops or volatile 64-bit reads to force visibility. These are subtle memory-ordering/data-coherency areas; command execution failures can present as firmware timeouts rather than local C errors.

Several comments warn that command IDs are stable. Adding new features should append IDs and fields rather than reuse reserved space unless firmware explicitly supports the change.

## Test Signals

Useful validation includes kernel build coverage for every consumer that constructs DMUB commands, static assertions that every inbox/outbox union remains 64 bytes, firmware compatibility tests for command IDs and payload sizes, boot tests that verify scratch status/boot option interpretation, GPINT STOP_FW/version/residency tests, AUX/HPD/DPIA outbox notification tests, ABM/PSR/Replay feature enablement tests, and ringbuffer wrap/full/empty tests. Runtime signals include DMUB firmware boot status, mailbox ready bit, command timeout counters, outbox notifications, scratch fault registers, trace-buffer entries, and display feature behavior such as PSR, Replay, ABM, DPIA, and cursor offload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/inc/dmub_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/inc/dmub_trace_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/inc/dmub_trace_buffer.h

## Purpose

`dmub_trace_buffer.h` defines a compact firmware trace-buffer format for DMCUB/DMUB. It provides trace event codes for boot, PHY initialization, firmware loading, idle, performance tracing, and power-gating completion, plus a fixed-size buffer layout that the driver can parse after firmware writes trace entries.

## Important APIs, Types, And Constants

The header includes `dmub_cmd.h`, so it inherits the fixed-width types used by the broader DMUB ABI. `LOAD_DMCU_FW` and `LOAD_PHY_FW` identify firmware load categories.

`enum dmucb_trace_code` contains event identifiers such as `DMCUB__MAIN_BEGIN`, PHY init/load start/end states, DMCU ERAM/ISR load start/end states, `DMCUB__MAIN_IDLE`, `DMCUB__PERF_TRACE`, and `DMCUB__PG_DONE`.

`struct dmcub_trace_buf_entry` contains a trace code, a tick count, and two event-specific 32-bit parameters. `TRACE_BUF_SIZE` is fixed at 1024 bytes. `PERF_TRACE_MAX_ENTRY` computes the number of entries after an 8-byte buffer header. `struct dmcub_trace_buf` stores `entry_count`, `clk_freq`, and the trace entries.

## Control Flow And Data Flow

Firmware writes entries into the trace buffer as boot and runtime milestones occur. Driver-side diagnostic code can map or copy the buffer, interpret `entry_count` and `clk_freq`, and convert each entry's tick count into timing information. The event code selects how to interpret `param0` and `param1`.

## State And Persistence Behavior

The buffer is a persistent diagnostic memory region across the firmware session. It is bounded to 1 KiB and does not include locking or wrap semantics in this header. Consumers must treat `entry_count` as firmware-owned and validate it against `PERF_TRACE_MAX_ENTRY`.

## Dependencies And Integration Points

This header integrates with DMUB firmware diagnostics, `dmub_cmd.h` trace entry definitions, the DMUB service trace/outbox paths, and any driver debugfs or timeout reporting code that dumps DMCUB trace data. It must stay layout-compatible with firmware trace writers.

## Risks And Edge Cases

The enum name is `dmucb_trace_code`, while most of the subsystem uses DMUB/DMCUB naming, so searchability can be uneven. `entry_count` can be corrupt or firmware-controlled, so readers should clamp it. The fixed 1 KiB size limits trace depth and makes event loss possible during long boot/runtime sequences.

## Test Signals

Test signals include nonzero `entry_count` after firmware boot, expected begin/end event ordering for PHY and DMCU loads, plausible `tick_count` deltas when `clk_freq` is set, and correct behavior when the buffer is empty or full. Timeout diagnostics should include these entries when firmware hangs during boot or PHY initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/inc/dmub_trace_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/Makefile

## Purpose

This Makefile fragment enumerates DMUB service and generation-specific source objects and appends them to the AMD display build. It is the build integration point for the DMUB service layer and hardware-family implementations.

## Important APIs, Types, And Functions

The `DMUB` variable starts with common service objects (`dmub_srv.o`, `dmub_srv_stat.o`, `dmub_reg.o`) and then appends generation objects from DCN20 through DCN42: `dmub_dcn20.o`, `dmub_dcn21.o`, `dmub_dcn30.o`, `dmub_dcn301.o`, `dmub_dcn302.o`, `dmub_dcn303.o`, `dmub_dcn31.o`, `dmub_dcn314.o`, `dmub_dcn315.o`, `dmub_dcn316.o`, `dmub_dcn32.o`, `dmub_dcn35.o`, `dmub_dcn351.o`, `dmub_dcn36.o`, `dmub_dcn401.o`, and `dmub_dcn42.o`.

`AMD_DAL_DMUB` prefixes those object names with `$(AMDDALPATH)/dmub/src/`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DMUB)` adds them to the overall display driver compilation list.

## Control Flow And Data Flow

There is no runtime control flow. Build-time flow is variable assembly: object names are collected, path-prefixed, and handed to the parent AMD display make infrastructure.

## State And Persistence Behavior

The file persists build membership only. Adding or removing a DMUB generation source changes which register tables and hardware function implementations are linked into the display driver.

## Dependencies And Integration Points

The fragment depends on parent make variables `AMDDALPATH` and `AMD_DISPLAY_FILES`. It integrates all DMUB source files with the broader AMDGPU display build. The generation objects correspond to ASIC-specific function tables selected by service creation code elsewhere.

## Risks And Edge Cases

If a new DMUB generation source is added but not listed here, it will not be compiled into the driver. If an object is listed without its source or with missing generated register headers, the AMD display build fails. Ordering is mostly not runtime-significant, but common service objects must be compiled and linked along with generation implementations.

## Test Signals

Primary signals are successful kernel/module builds, presence of the expected DMUB objects in the build log, and successful linking of symbols such as generation register tables and hardware functions. Runtime validation is indirect: ASIC-specific DMUB initialization must find the expected function implementation after build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c

## Purpose

`dmub_dcn20.c` implements the DCN 2.0 DMUB hardware access layer. It provides the DCN20 register table and hardware functions used by `dmub_srv` to reset the microcontroller, load firmware through code windows, configure memory windows and mailboxes, send GPINT commands, read firmware status, set boot options, and collect diagnostic data.

## Important APIs, Types, And Functions

`dmub_srv_dcn20_regs` maps common DMUB register offsets, masks, and shifts using DCN 2.0 generated register headers. It is consumed through `dmub->regs`.

Private helpers are `dmub_dcn20_get_fb_base_offset`, which obtains framebuffer base/offset either from `dmub->soc_fb_info` or hardware registers, and `dmub_dcn20_translate_addr`, which converts input GPU addresses into DMUB-visible offsets.

Reset and boot functions include `dmub_dcn20_reset`, `dmub_dcn20_reset_release`, `dmub_dcn20_backdoor_load`, `dmub_dcn20_setup_windows`, `dmub_dcn20_enable_dmub_boot_options`, and `dmub_dcn20_skip_dmub_panel_power_sequence`.

Mailbox functions include `dmub_dcn20_setup_mailbox`, `dmub_dcn20_get_inbox1_wptr`, `dmub_dcn20_get_inbox1_rptr`, `dmub_dcn20_set_inbox1_wptr`, `dmub_dcn20_setup_out_mailbox`, `dmub_dcn20_get_outbox1_wptr`, `dmub_dcn20_set_outbox1_rptr`, `dmub_dcn20_setup_outbox0`, `dmub_dcn20_get_outbox0_wptr`, and `dmub_dcn20_set_outbox0_rptr`.

Status, GPINT, and diagnostics are handled by `dmub_dcn20_is_hw_init`, `dmub_dcn20_is_supported`, `dmub_dcn20_set_gpint`, `dmub_dcn20_is_gpint_acked`, `dmub_dcn20_get_gpint_response`, `dmub_dcn20_get_fw_boot_status`, `dmub_dcn20_use_cached_inbox`, `dmub_dcn20_use_cached_trace_buffer`, `dmub_dcn20_get_current_time`, and `dmub_dcn20_get_diagnostic_data`. In this source, `dmub_dcn20_use_cached_inbox` rejects a known unsupported firmware version range from 1.0.0 through 1.10.0.

## Control Flow And Data Flow

Reset flow checks `DMCUB_SOFT_RESET`. If firmware is not already in reset, the driver sends `DMUB_GPINT__STOP_FW`, waits up to 30 polling iterations for GPINT acknowledgement, waits for scratch7 to equal `DMUB_GPINT__STOP_FW_RESPONSE`, clears the GPINT command, then forces reset by setting DMCUB soft reset, disabling DMCUB, resetting DMUIF, clearing inbox/outbox pointers, and clearing scratch0.

Reset release flow deasserts DMUIF reset, writes a masked PSP version into scratch15, enables DMCUB and traceport, then clears soft reset.

Backdoor load flow asserts secure reset, configures MEM read/write space, translates CW0/CW1 addresses from framebuffer base/offset space, programs region offsets/base/top/enables, and releases secure reset with memory unit ID `0x20`.

Window setup programs CW2 through CW6. CW2 can be disabled by a base==top sentinel. CW4 is programmed either through REGION3_CW4 for cached-inbox-capable firmware or through legacy REGION4. CW5 is also mirrored through REGION5. CW6 is programmed normally. `region6` is unused in this generation.

Mailbox setup uses the firmware-version decision in `dmub_dcn20_use_cached_inbox`. Newer firmware uses the caller-provided base; unsupported cached-inbox firmware uses legacy fixed addresses `0x80000000` for inbox1 and `0x80002000` for outbox1. Sizes are computed as top minus base.

GPINT acknowledgement flow writes GPINT data-in, then treats acknowledgement as firmware clearing the status field while preserving command and parameter bits.

Diagnostic flow preserves existing timeout info, zeros `dmub->debug`, records firmware version, scratch0-15, fault addresses, inbox and outbox pointers/sizes, and selected enable/reset/trace/window bits.

## State And Persistence Behavior

This file mutates hardware register state: DMUB reset bits, secure reset, code window mappings, mailbox bases/sizes/pointers, scratch registers, GPINT data-in, and debug snapshots in `dmub->debug`. It also uses `dmub->fw_version`, `dmub->psp_version`, and optional `dmub->soc_fb_info` as persistent service state.

Mailbox pointer reset is part of hardware reset, so pending commands are discarded on reset. Diagnostic data is overwritten each capture but preserves timeout metadata.

## Dependencies And Integration Points

The file depends on `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn20.h`, DCN 2.0 offset/shift/mask generated headers, `soc15_hw_ip.h`, and `vega10_ip_offset.h`. It integrates with `dmub_srv_hw_init`, `dmub_srv_hw_reset`, `dmub_srv_fb_cmd_execute`, GPINT service helpers, firmware boot polling, and timeout diagnostics through `struct dmub_srv_hw_funcs`.

## Risks And Edge Cases

The STOP_FW wait loops use only 30 iterations without `udelay`, relying on register access latency. A slow firmware stop can fall through to forced reset. Address translation assumes `addr_in >= fb_base` in the relevant address space; bad framebuffer base/offset inputs can produce wrapped addresses.

CW4 behavior depends on firmware version. Misreporting firmware version can place inbox/outbox in the wrong address window. The fixed legacy mailbox bases are magic constants and must match firmware expectations. Pointer register access comments note unlocked outbox1 access from DAL and DC, so consumers must avoid racing semantics.

`dmub_dcn20_enable_dmub_boot_options` writes zeroed boot options, ignoring `params`; later generations add more boot-option behavior. Changes to shared service code must account for this generation difference.

## Test Signals

Validation includes DCN20 boot on hardware or emulation, successful firmware mailbox-ready status after backdoor load and reset release, GPINT STOP_FW acknowledgement and scratch response, inbox/outbox pointer progression during command execution, correct behavior across firmware versions 1.0.0 through 1.10.0 versus newer cached-inbox firmware, and diagnostic dumps containing scratch/fault/pointer data after timeout. Build tests must confirm generated register names match DCN20 headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.h

## Purpose

`dmub_dcn20.h` declares the common DCN20-era DMUB register map and hardware operations. Later DCN generation headers include it when they reuse the common register layout and function prototypes.

## Important APIs, Types, And Functions

`DMUB_COMMON_REGS()` lists common DMCUB registers: control, memory/security control, inbox0/inbox1, outbox0/outbox1, REGION3 code windows CW0-CW7, REGION4/5, scratch registers, GPINT data-in, display pipe disable, DMUIF soft reset, framebuffer base/offset, interrupt acknowledge, timer, and fault address registers.

`DMCUB_INTERNAL_REGS()` is empty in this header but acts as an extension hook for generation-specific internal registers. `DMUB_COMMON_FIELDS()` lists field names used to generate shifts and masks for DMCUB enable/reset/traceport, memory spaces, security reset/unit/status, region top/enable fields, pipe enable support, DMUIF reset, framebuffer base/offset, and outbox interrupt ack.

The header defines `struct dmub_srv_common_reg_offset`, `struct dmub_srv_common_reg_shift`, `struct dmub_srv_common_reg_mask`, and `struct dmub_srv_common_regs`. `dmub_srv_dcn20_regs` is exported by `dmub_dcn20.c`.

It declares DCN20 hardware functions for reset, reset release, backdoor load, window setup, inbox/outbox setup and pointer access, support/init checks, GPINT access, boot options, panel-power sequencing skip, firmware boot status, cached inbox/trace-buffer policy, current timer reads, and diagnostic capture.

## Control Flow And Data Flow

This header supplies the static register/field lists that `dmub_dcn20.c` expands into offset, mask, and shift tables. Service code stores the resulting table in `dmub->regs`; `dmub_reg.h` macros use it to translate generic register names into MMIO accesses.

Function declarations define the operations that the service layer can place in `struct dmub_srv_hw_funcs`. Runtime flow is therefore indirect: `dmub_srv` calls function pointers, and DCN20 implementations perform register-level operations.

## State And Persistence Behavior

The header itself has no state. It defines the shape of persistent register-table objects and the API surface used to mutate DMUB hardware state in the implementation.

## Dependencies And Integration Points

It includes `../inc/dmub_cmd.h` for `union dmub_gpint_data_register`, firmware status/options, and DMUB address/window/region types that are defined in nearby service headers. It forward-declares `struct dmub_srv`. DCN21, DCN30, DCN301, DCN302, and DCN303 headers include this header to inherit the common register and function declarations.

## Risks And Edge Cases

Changing `DMUB_COMMON_REGS()` or `DMUB_COMMON_FIELDS()` affects every generation that uses `struct dmub_srv_common_regs`. A field missing from the list cannot be accessed through the common `REG_*` macros. A field added here must exist in all generated register headers for every common-generation user or builds will fail.

The declaration `dmub_dcn20_init` is present in this header, but the corresponding definition is not in the researched `dmub_dcn20.c` file. That may be supplied elsewhere or unused by this tree; it is a symbol-consistency point to check during build/link validation.

## Test Signals

Signals include successful compilation of every generation that includes this header, correct expansion of register tables for DCN20 and derivative generations, link success for declared functions that are referenced by function tables, and runtime register access sanity during DMUB reset, boot, mailbox setup, and diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c

## Purpose

`dmub_dcn21.c` provides the DCN 2.1 DMUB register table. It does not implement new hardware behavior beyond table construction; it allows the common DCN20 hardware functions to operate on DCN21/Renoir register offsets and masks.

## Important APIs, Types, And Functions

The only exported object is `dmub_srv_dcn21_regs`, a `struct dmub_srv_common_regs` initialized by expanding `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()` through generated DCN 2.1 register macros.

## Control Flow And Data Flow

At compile time, `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT` macros expand names from `dmub_dcn20.h` into DCN21-specific offset/mask/shift constants. At runtime, service code can point `dmub->regs` at `dmub_srv_dcn21_regs` and reuse common hardware functions.

## State And Persistence Behavior

The file defines immutable register metadata. It does not read or write hardware directly and does not maintain runtime state.

## Dependencies And Integration Points

It depends on `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn21.h`, generated `dcn_2_1_0_offset.h`, generated `dcn_2_1_0_sh_mask.h`, and `renoir_ip_offset.h`. The `BASE_INNER(seg)` macro uses `DMU_BASE__INST0_SEG##seg`, reflecting this generation's base naming.

## Risks And Edge Cases

The risk is register-definition mismatch. If `DMUB_COMMON_REGS()` names a register absent from DCN21 generated headers, build fails. If an offset or mask differs from hardware expectations, common DMUB functions will program the wrong registers.

## Test Signals

Signals include clean build against Renoir/DCN21 generated headers and successful DMUB boot/mailbox operation on DCN21 hardware using the inherited common function set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.h

## Purpose

`dmub_dcn21.h` is the public declaration header for the DCN21 DMUB register table. It inherits the DCN20 common register/function model and exports the DCN21 table symbol.

## Important APIs, Types, And Functions

The header includes `dmub_dcn20.h` and declares `extern const struct dmub_srv_common_regs dmub_srv_dcn21_regs`.

## Control Flow And Data Flow

There is no runtime control flow in the header. Its declaration lets service creation code or generation-selection tables bind DCN21 hardware to the common DMUB register-access layer.

## State And Persistence Behavior

No state is owned here. The externally declared register table is immutable and generation-specific.

## Dependencies And Integration Points

The dependency on `dmub_dcn20.h` means DCN21 uses the common DCN20 register struct layout and function declarations. Integration is through `dmub_srv` hardware setup code that chooses `dmub_srv_dcn21_regs` for DCN21 ASICs.

## Risks And Edge Cases

Any DCN21-specific hardware behavior not represented by the common DCN20 functions would require additional declarations here. As written, this header assumes register-table substitution is sufficient.

## Test Signals

Build/link success for `dmub_srv_dcn21_regs` and runtime DMUB initialization on DCN21 hardware are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c

## Purpose

`dmub_dcn30.c` provides DCN 3.0 DMUB register metadata and overrides the firmware backdoor-load/window-setup behavior where DCN30 differs from DCN20. It targets Sienna Cichlid style register definitions.

## Important APIs, Types, And Functions

`dmub_srv_dcn30_regs` is the exported common register table for DCN30. Private helpers `dmub_dcn30_get_fb_base_offset` and `dmub_dcn30_translate_addr` mirror DCN20 address translation for firmware load windows.

The exported hardware functions are `dmub_dcn30_backdoor_load` and `dmub_dcn30_setup_windows`.

## Control Flow And Data Flow

Backdoor load reads or uses cached framebuffer base/offset, asserts secure reset, translates CW0 and CW1 addresses, programs REGION3 CW0/CW1 offsets, bases, tops, and enables, then releases secure reset with memory unit ID `0x20`. Unlike DCN20, it does not program `DMCUB_MEM_CNTL` read/write space because that control does not exist on this generation.

Window setup differs more strongly from DCN20. A comment states Sienna Cichlid has hardwired virtual addressing for CW2-CW7, so it uses each window's offset directly instead of translating through framebuffer base/offset. CW2 is disabled when base equals top. CW3, CW5, and CW6 are programmed through REGION3. CW4 uses REGION3_CW4 when `dmub_dcn20_use_cached_inbox()` allows it, otherwise legacy REGION4. CW5 is mirrored into REGION5 as in DCN20.

## State And Persistence Behavior

The file mutates secure reset and code-window MMIO state. It relies on `dmub->soc_fb_info` for optional address translation during backdoor load and `dmub->fw_version` indirectly for cached inbox policy through the DCN20 helper.

## Dependencies And Integration Points

It depends on `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn20.h`, `dmub_dcn30.h`, `sienna_cichlid_ip_offset.h`, and generated DCN 3.0 offset/mask headers. It integrates with the shared `dmub_srv_hw_init` flow via generation-specific function pointers for backdoor load and setup windows, while other operations may reuse DCN20 functions.

## Risks And Edge Cases

Using direct offsets for CW2-CW7 is generation-specific. Applying this function to a generation requiring framebuffer translation would corrupt window programming. Conversely, using DCN20 window translation on DCN30 would break hardwired virtual addressing.

The cached-inbox firmware-version decision is inherited from DCN20. If DCN30 firmware has different constraints, the shared helper could choose the wrong CW4/REGION4 path.

## Test Signals

Validation includes successful DCN30 build with Sienna Cichlid generated headers, firmware backdoor load success, mailbox setup after direct CW programming, command execution through inbox/outbox, and regression tests on firmware versions around the cached-inbox unsupported range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.h

## Purpose

`dmub_dcn30.h` declares the DCN30 DMUB register table and the DCN30-specific hardware functions that override DCN20 behavior.

## Important APIs, Types, And Functions

The header includes `dmub_dcn20.h`, declares `extern const struct dmub_srv_common_regs dmub_srv_dcn30_regs`, and declares `dmub_dcn30_backdoor_load` plus `dmub_dcn30_setup_windows`.

## Control Flow And Data Flow

The declarations allow hardware-function tables to select DCN30-specific firmware loading and window setup while keeping the rest of the common DCN20-style DMUB operation surface.

## State And Persistence Behavior

No state is owned in the header. The declared functions mutate hardware state in `dmub_dcn30.c`.

## Dependencies And Integration Points

It depends on the common DCN20 register/function declarations. Service creation code for DCN30 ASICs should use `dmub_srv_dcn30_regs` and substitute the two declared function overrides.

## Risks And Edge Cases

If service code forgets to use the DCN30 overrides, CW2-CW7 addressing can be programmed with the wrong address model. If future DCN30 variants need more overrides, this header will need to expand.

## Test Signals

Build/link success for `dmub_srv_dcn30_regs`, `dmub_dcn30_backdoor_load`, and `dmub_dcn30_setup_windows`, plus runtime DMUB boot on DCN30 hardware, are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c

## Purpose

`dmub_dcn301.c` provides the DCN 3.0.1 DMUB register table for Van Gogh style hardware. It does not implement additional hardware operations in this file.

## Important APIs, Types, And Functions

The exported object is `dmub_srv_dcn301_regs`, a `struct dmub_srv_common_regs` populated by expanding the common DMUB register and field macros against DCN 3.0.1 generated offset/mask/shift definitions.

## Control Flow And Data Flow

Runtime hardware access is indirect. Service code points `dmub->regs` at `dmub_srv_dcn301_regs` and uses common function implementations from the DCN20 model unless another table overrides them elsewhere.

## State And Persistence Behavior

The file defines immutable register metadata only.

## Dependencies And Integration Points

It depends on `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn301.h`, generated DCN 3.0.1 headers, and `vangogh_ip_offset.h`. It integrates with ASIC selection logic that chooses DCN301 register metadata for DMUB operations.

## Risks And Edge Cases

The file assumes common DCN20-style function behavior is enough for DCN301. Any DCN301-specific window, reset, mailbox, or boot-option behavior would need explicit functions added elsewhere.

## Test Signals

Signals include clean build with Van Gogh register headers, successful link of `dmub_srv_dcn301_regs`, and DMUB boot/command execution on DCN301 hardware using the selected table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.h

## Purpose

`dmub_dcn301.h` declares the DCN301 DMUB register table and inherits common DCN20 declarations.

## Important APIs, Types, And Functions

It includes `dmub_dcn20.h` and declares `extern const struct dmub_srv_common_regs dmub_srv_dcn301_regs`.

## Control Flow And Data Flow

There is no executable flow. The declaration supports generation selection in DMUB service setup.

## State And Persistence Behavior

No state is owned by this header.

## Dependencies And Integration Points

The header's dependency on `dmub_dcn20.h` means DCN301 uses the common DMUB register structure and hardware function API. Integration occurs wherever ASIC-specific setup maps Van Gogh/DCN301 to `dmub_srv_dcn301_regs`.

## Risks And Edge Cases

The empty hardware-functions section signals that this generation is register-table-only in this subset. Any undocumented generation behavior would be easy to miss unless covered by runtime tests.

## Test Signals

Build/link success and runtime DMUB initialization on DCN301 hardware are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c

## Purpose

`dmub_dcn302.c` provides the DCN 3.0.2 DMUB register table, using Dimgrey Cavefish IP offsets with DCN 3.0 generated register definitions. It has no unique runtime functions in this file.

## Important APIs, Types, And Functions

The exported object is `dmub_srv_dcn302_regs`, a `struct dmub_srv_common_regs` containing offsets, masks, and shifts for the common DMUB register/field set.

## Control Flow And Data Flow

The file constructs the table at compile time using `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT`. Runtime control flow is delegated to common DMUB hardware functions that consume `dmub->regs`.

## State And Persistence Behavior

It defines immutable metadata and no runtime state.

## Dependencies And Integration Points

Dependencies are `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn302.h`, `dimgrey_cavefish_ip_offset.h`, and DCN 3.0 generated offset/mask headers. Integration is through generation-specific ASIC setup.

## Risks And Edge Cases

DCN302 uses DCN 3.0 register headers rather than a distinct 3.0.2 register header in this file. That is intentional if the register block is shared, but it is a maintenance risk if the hardware diverges.

## Test Signals

Signals include compile success against Dimgrey Cavefish offsets, link success for `dmub_srv_dcn302_regs`, and hardware boot/DMUB command execution on DCN302 ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.h

## Purpose

`dmub_dcn302.h` declares the DCN302 DMUB register table and reuses the DCN20 common DMUB API surface.

## Important APIs, Types, And Functions

It includes `dmub_dcn20.h` and declares `extern const struct dmub_srv_common_regs dmub_srv_dcn302_regs`.

## Control Flow And Data Flow

No direct control flow exists. Service setup uses the declaration to bind DCN302 hardware to the common register table model.

## State And Persistence Behavior

The header owns no runtime state.

## Dependencies And Integration Points

The integration point is ASIC selection code that uses `dmub_srv_dcn302_regs`. The header depends on common DCN20 declarations for type definitions.

## Risks And Edge Cases

As with DCN301, the hardware-functions section is empty. Tests must prove common behavior is sufficient for this generation.

## Test Signals

Build/link coverage and DMUB initialization on DCN302 hardware are the core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c

## Purpose

`dmub_dcn303.c` provides the DCN 3.0.3 DMUB register table. It is a register-metadata-only generation file in this subset.

## Important APIs, Types, And Functions

The exported object is `dmub_srv_dcn303_regs`, initialized as a `struct dmub_srv_common_regs` by expanding the common DMUB register and field macros with DCN 3.0.3 generated headers.

## Control Flow And Data Flow

Runtime flow is indirect through the service layer. The file supplies offsets/masks/shifts so common DMUB functions can access the correct DCN303 registers.

## State And Persistence Behavior

No runtime state is maintained. The register table is immutable.

## Dependencies And Integration Points

It depends on `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn303.h`, `sienna_cichlid_ip_offset.h`, and DCN 3.0.3 generated offset/mask headers. It integrates with generation selection code for DCN303 ASICs.

## Risks And Edge Cases

This file uses Sienna Cichlid IP offsets with DCN 3.0.3 register definitions. Wrong pairing would cause register access errors. Since there are no custom functions, runtime tests must catch any generation behavior not handled by common functions.

## Test Signals

Clean build, link success for `dmub_srv_dcn303_regs`, and successful DMUB boot and mailbox command flow on DCN303 hardware are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.h

## Purpose

`dmub_dcn303.h` declares the DCN303 DMUB register table and inherits the common DCN20 API model.

## Important APIs, Types, And Functions

It includes `dmub_dcn20.h` and declares `extern const struct dmub_srv_common_regs dmub_srv_dcn303_regs`.

## Control Flow And Data Flow

The header provides no runtime flow. It supports generation-selection code that binds DCN303 hardware to its register table.

## State And Persistence Behavior

No state is owned here.

## Dependencies And Integration Points

The dependency on `dmub_dcn20.h` pulls in common register structs and hardware operation declarations. The exported table symbol is implemented in `dmub_dcn303.c`.

## Risks And Edge Cases

The empty hardware-functions section means the generation has no local operation overrides in this subset. Any required DCN303-specific behavior must be implemented elsewhere or tests will expose initialization failures.

## Test Signals

Build/link success and runtime DMUB initialization on DCN303 hardware are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c

## Purpose

`dmub_dcn31.c` implements the DCN 3.1 DMUB hardware access layer. It is similar in role to `dmub_dcn20.c`, but uses a distinct DCN31 register table, different reset control register layout, additional GPINT data-out interrupt handling, richer boot option programming, and updated diagnostics.

## Important APIs, Types, And Functions

`dmub_srv_dcn31_regs` is the exported DCN31 register table. It is a `struct dmub_srv_dcn31_regs`, not `struct dmub_srv_common_regs`, because DCN31 adds `DMCUB_CNTL2`, `DMCUB_GPINT_DATAOUT`, interrupt enable/ack fields, inbox0 write-pointer field access, and `DMCUB_PWAIT_MODE_STATUS`.

Private helpers `dmub_dcn31_get_fb_base_offset` and `dmub_dcn31_translate_addr` perform framebuffer base/offset lookup and address translation for firmware load windows.

Hardware functions include `dmub_dcn31_reset`, `dmub_dcn31_reset_release`, `dmub_dcn31_backdoor_load`, `dmub_dcn31_setup_windows`, mailbox setup and pointer accessors, support/init checks, `dmub_dcn31_is_psrsu_supported`, GPINT accessors, `dmub_dcn31_get_gpint_dataout`, firmware status/boot-option readers, boot-option writer, panel power-sequence skip, outbox0 setup/accessors, current timer read, diagnostic capture, and `dmub_dcn31_should_detect`.

## Control Flow And Data Flow

Reset flow checks `DMCUB_CNTL2.DMCUB_SOFT_RESET`. If firmware is running, it sends `DMUB_GPINT__STOP_FW`, waits up to 100000 microsecond-delayed iterations for GPINT ack, waits for scratch7 STOP_FW response, then waits for `DMCUB_PWAIT_MODE_STATUS` bit 0. If DMCUB is enabled, it asserts `DMCUB_CNTL2` soft reset, resets DMUIF, and disables DMCUB. It clears inbox1/outbox1/outbox0 pointers, scratch0, and GPINT data-in before boot.

Reset release deasserts DMUIF reset, writes masked PSP version to scratch15, enables DMCUB and traceport in `DMCUB_CNTL`, then clears `DMCUB_CNTL2.DMCUB_SOFT_RESET`.

Backdoor load translates and programs CW0/CW1 similarly to DCN20/DCN30, but without `DMCUB_MEM_CNTL` programming. Window setup ignores CW2 and `region6`, then directly programs CW3, CW4, CW5, REGION5, and CW6 using window offsets. Unlike DCN20/DCN30, CW4 is always programmed as REGION3_CW4 in this function.

Mailbox setup writes caller-provided inbox1/outbox1 bases directly with size as top minus base. Outbox0 is also directly based. GPINT data-in behavior mirrors DCN20, but GPINT data-out is read from `DMCUB_GPINT_DATAOUT` with interrupt disable, data clear, interrupt ack pulse, and interrupt re-enable.

Boot-option flow populates scratch14 from `dmub_srv_hw_params`: z10 disable, DPIA support/enable, USB4 CM version, DPIA HPD interrupt support, power optimization, HBR3 SSC/PLL overrides, DCN31B PHY mux selection, and DPIA bandwidth allocation disable.

Diagnostic flow captures scratch registers, fault addresses, inbox0/inbox1/outbox1 pointers and sizes, enable state, PWAIT state, soft/security reset state, traceport, and CW0/CW6 enable bits. `dmub_dcn31_should_detect` reads scratch0 and returns whether `DMUB_FW_BOOT_STATUS_BIT_DETECTION_REQUIRED` is set.

## State And Persistence Behavior

This file mutates DCN31 DMUB control registers, code windows, mailboxes, scratch registers, interrupt enable/ack state, GPINT data registers, and the service debug snapshot. It uses persistent `dmub->fw_version`, `dmub->psp_version`, `dmub->asic`, `dmub->soc_fb_info`, and hardware init state from the service layer.

The boot options written to scratch14 persist into firmware boot and influence firmware behavior. Diagnostic capture overwrites `dmub->debug` while preserving timeout metadata.

## Dependencies And Integration Points

Dependencies are `dmub_srv.h`, `dmub_reg.h`, `dmub_dcn31.h`, `yellow_carp_offset.h`, and generated DCN 3.1.2 register headers. It integrates with `dmub_srv` hardware initialization/reset, command execution, GPINT service functions, outbox notification handling, boot-status polling, PSR-SU feature checks, detection-required checks, and timeout diagnostics.

## Risks And Edge Cases

DCN31 reset has much longer waits than DCN20 and uses `udelay(1)`, so it can block for a noticeable time during a hung firmware stop. If PWAIT never appears, reset still proceeds as forced recovery. Clearing GPINT after pointer resets avoids accidental boot-time commands, but any concurrent GPINT user would be racing service reset.

`dmub_dcn31_is_hw_init` requires both DMCUB enable and scratch0 `dal_fw`; firmware that is enabled but has not updated scratch0 will be treated as not initialized. Boot option bits must match firmware interpretation exactly. `dmub_dcn31_get_gpint_dataout` temporarily disables GPINT interrupt handling, so ordering matters if interrupts can arrive concurrently.

Window setup ignores CW2 entirely; this is correct only if DCN31 firmware/service memory layout does not need CW2 in this path.

## Test Signals

Validation includes DCN31/Yellow Carp build, boot and reset recovery on hardware, scratch0 DAL firmware and mailbox-ready status, STOP_FW GPINT ack/response/PWAIT sequencing, direct mailbox pointer progression, GPINT data-out interrupt ack behavior, DPIA/USB4 boot option behavior, PSR-SU support gating at firmware version 4.0.59, detection-required scratch bit handling, and timeout diagnostics containing PWAIT/outbox1 information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c -->

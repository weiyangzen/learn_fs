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

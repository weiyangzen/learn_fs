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

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

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.h

Purpose: declares the DCN42 DMUB register inventory and API. It merges DCN35 fields such as `DMU_CLK_CNTL` with DCN401 register-mailbox and `HOST_INTERRUPT_CSR` fields, while dropping `CC_DC_PIPE_DIS` support probing from the register list.

Important APIs and control flow: `DMUB_DCN42_REGS()` covers DMCUB control, mailboxes, region3/4/5/6, scratch0-21, GPINT, MMHUBBUB reset, FB base/offset, timer/fault/TMR, interrupts, clock control, register inbox/outbox message/response registers, and host interrupt CSR. `DMUB_DCN42_FIELDS()` provides masks/shifts for window enables, reset/control, FB/TMR, GPINT interrupt, PWAIT, LONO gates, and register inbox/outbox interrupt bits. Declarations are grouped by initialization, reset, firmware loading, mailbox, register mailbox, GPINT, status, boot status/options, timing, diagnostics, and pre-OS info.

State and persistence behavior: no direct state; `struct dmub_srv_dcn42_regs` is mutable and initialized per device. Runtime values persist in DMCUB registers and service-owned state.

Dependencies and integration points: includes `dmub_dcn35.h` and `dmub_dcn401.h`; implemented by `dmub_dcn42.c` and assigned by `dmub_srv_hw_setup()` for DCN42.

Risks and test signals: risks include a large macro surface drifting from generated DCN42 headers, duplicated declaration groups diverging from implementation, and unconditional support behavior needing service-layer awareness. Test signals are clean compile, initialized offsets/masks, working clock-gate release, and register-mailbox interrupt coverage on DCN42 hardware.

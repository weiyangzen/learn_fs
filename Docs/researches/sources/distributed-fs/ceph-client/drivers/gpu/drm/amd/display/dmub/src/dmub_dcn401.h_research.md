# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.h

Purpose: declares the DCN401 DMUB register inventory and hardware API, including register-mailbox registers and host interrupt fields absent from older DCN31/32/35 headers.

Important APIs and control flow: `DMUB_DCN401_REGS()` includes DMCUB control, mailboxes, region windows, scratch0-17, GPINT, support/reset/FB/timer/fault/TMR registers, interrupt enable/ack/status, `DMCUB_REG_INBOX0_RDY`, `DMCUB_REG_INBOX0_MSG0..14`, `DMCUB_REG_INBOX0_RSP`, `DMCUB_REG_OUTBOX0_RDY`, `DMCUB_REG_OUTBOX0_MSG0`, `DMCUB_REG_OUTBOX0_RSP`, and `HOST_INTERRUPT_CSR`. `DMUB_DCN401_FIELDS()` includes normal DMUB fields plus register inbox/outbox interrupt status, ack, and enable fields. Function declarations cover both legacy framebuffer mailbox callbacks and the register inbox/outbox helpers.

State and persistence behavior: no state in the header. The const `dmub_srv_dcn401_regs` table maps the declared fields to runtime MMIO accesses.

Dependencies and integration points: includes `dmub_dcn31.h`; implemented by `dmub_dcn401.c` and bound by `dmub_srv.c` for `DMUB_ASIC_DCN401`.

Risks and test signals: risks include field-list drift with DCN 4.1 generated headers, missing register-mailbox callbacks if `dmub_srv_hw_funcs` changes, and interrupt field polarity mismatches. Test signals include compile coverage and command/response traffic through both FB and register inbox paths.

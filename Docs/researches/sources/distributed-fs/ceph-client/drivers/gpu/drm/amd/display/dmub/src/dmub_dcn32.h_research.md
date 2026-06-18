# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.h

Purpose: declares the DCN32 DMUB register inventory and callback surface. It extends DCN31 with region6, scratch16-23, GPINT datain0, DMCUB region3 TMR AXI-space selection, and dynamic register-table storage.

Important APIs and control flow: `DMUB_DCN32_REGS()` and `DMUB_DCN32_FIELDS()` generate offset/mask/shift structs for `struct dmub_srv_dcn32_regs`. Function declarations cover reset/release, normal/ZFB backdoor load, window setup, inbox1/outbox1/outbox0 mailbox helpers, support/init detection, GPINT, boot options, diagnostics, system-memory configuration, inbox0 command/ack helpers, SubVP surface save, and dynamic register initialization.

State and persistence behavior: no direct state, but the non-const register table is filled per device by `dmub_srv_dcn32_regs_init()` using `ctx->dcn_reg_offsets`. Runtime persistence lives in DMCUB registers and scratch fields.

Dependencies and integration points: includes `dmub_dcn31.h` for common DMUB types. `dmub_srv.c` owns the static `dmub_srv_dcn32_regs` storage and assigns this API for DCN32/DCN321.

Risks and test signals: risks include dynamic offset initialization being skipped, macro mismatch with generated DCN32 headers, and service callbacks assuming function declarations remain in sync with the implementation. Test signals include `init_reg_offsets` invocation before first MMIO access, compile coverage, and operational inbox0/inbox1/outbox/GPINT paths on DCN32 hardware.

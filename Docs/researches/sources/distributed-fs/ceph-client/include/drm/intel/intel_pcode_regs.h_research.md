# sources/distributed-fs/ceph-client/include/drm/intel/intel_pcode_regs.h

Purpose: defines Intel PCODE mailbox MMIO register, command fields, status codes, and mailbox command payload helpers used for power, display frequency, memory latency, SAGV, CDCLK, TCCOLD, HDCP key load, and frequency configuration.

Important APIs/types/functions: `GEN6_PCODE_MAILBOX` and fields such as ready bit, param masks, command mask, and error values are central. Command constants include RC6 voltage read/write, display frequency change request, memory latency reads, HDCP keys, CDCLK control, min frequency table, OC params, memory subsystem info, SAGV configuration, TCCOLD, IPS, dynamic duty cycle, DG1 status, power setup, SAGV block time, and XeHP frequency config. Helpers encode/decode RC6 VID and prepare CDCLK/pipe-count/voltage fields.

Control flow: pcode interface code writes mailbox command/params, waits for ready/status, decodes replies and errors, and retries or fails based on platform-specific status values.

State and persistence: PCODE firmware holds persistent platform power/frequency state; mailbox requests transiently update or query it.

Dependencies and integration: expects `_MMIO`, `REG_GENMASK`, `REG_BIT`, and `REG_FIELD_PREP`. Integrated by Intel display power management, CDCLK, SAGV, IPS, and GT frequency code.

Risks and test signals: command/status values vary by generation. Wrong masks or status interpretation can hang display power changes or memory frequency transitions. Test pcode timeout/error paths, CDCLK transitions, SAGV enable/disable, TCCOLD entry/exit, and platform-specific mailbox command coverage.

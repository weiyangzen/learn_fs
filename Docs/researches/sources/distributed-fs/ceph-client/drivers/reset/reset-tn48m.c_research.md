# sources/distributed-fs/ceph-client/drivers/reset/reset-tn48m.c

Purpose: Delta TN48M CPLD reset controller for board-level CPU, MAC, PHY, and PoE reset lines.

Important APIs/types/functions: `tn48m_resets[]` maps binding IDs to bits in `TN48M_RESET_REG`. `tn48m_control_reset()` clears a bit then polls until hardware sets it again, implementing a pulse. `tn48m_control_status()` returns asserted when the bit is clear. Probe obtains the parent regmap and registers `.reset` and `.status` ops.

Control flow: platform child of a regmap-providing CPLD binds, registers six resets, and reset consumers trigger poll-based reset pulses.

State and persistence: parent CPLD register state persists; driver holds parent regmap and rcdev only.

Dependencies and integration: parent device regmap, Delta reset dt-bindings, platform bus, reset framework.

Risks and test signals: `regmap_update_bits()` return value is ignored before polling. Poll timeout is 125 ms. Test parent regmap absence, poll timeout, status polarity, and each binding ID bit.

# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.11.c

Purpose: Defines the GSI register descriptor table for IPA v4.11 / GSI v2.11 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v4_11`. Compared with older v4.0-style maps, channel/event blocks move to the `0x0000f000`/`0x00012000` layout, QoS gains prefetch and byte-doorbell fields, `GENERIC_CMD` includes parameter bits, and `HW_PARAM_2` exposes RD/WR-engine and inter-EE capability bits.

Control flow and integration: Common GSI channel, event, interrupt, generic command, and capability code consumes this table through register helper lookups. The descriptors determine how channel state and event ring state are packed into MMIO writes.

State and persistence: Static register descriptors only. Values programmed using them persist in hardware register state and are tied to AP execution-environment offsets.

Dependencies: Uses common field IDs from `gsi_reg.h`; correctness depends on those IDs matching every `fmask` array index and `reg_array` entry.

Risks: v4.11 is close to v4.5/v4.9 but not identical; `GENERIC_PARAMS` exists here while some earlier v4 maps do not. QoS field differences can alter prefetch and doorbell semantics. Wrong base offset will prevent interrupts and commands from reaching the AP EE block.

Test signals: Probe v4.11 hardware, exercise generic commands with parameters, verify `HW_PARAM_2` capability decode, open channels, run traffic, and confirm IRQ clear/mask behavior.

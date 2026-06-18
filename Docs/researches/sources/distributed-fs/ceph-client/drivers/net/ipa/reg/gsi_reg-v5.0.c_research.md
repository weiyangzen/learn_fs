# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v5.0.c

Purpose: Defines the GSI register descriptor table for IPA v5.0 / GSI v3.0 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v5_0`. The map shifts to the v5 `0x12000 * GSI_EE_AP` execution-environment aperture, widens channel protocol/channel ID/ring length fields, moves event EE bits, adds `CH_ERINDEX`, `LOW_LATENCY_EN`, `GENERIC_PARAMS`, and `HW_PARAM_4`, and keeps the core channel/event/doorbell/interrupt/error descriptors.

Control flow and integration: GSI core code uses this map to program v5 channel contexts, event contexts, QoS, commands, generic commands, interrupt blocks, and capability discovery. `HW_PARAM_4` exposes event-per-EE and IRAM protocol-count style data not present in older maps.

State and persistence: Static ABI metadata only. Programmed GSI channel and event state persists in hardware while channels are active.

Dependencies: Depends on the same shared `gsi_reg.h` IDs as older maps, but field masks differ substantially; version dispatch must select this table for v5-style hardware.

Risks: The v5 field layout is not backward compatible with v3/v4 layouts. Using older encode/decode assumptions truncates channel IDs or ring lengths. The larger EE aperture and reordered IRQ offsets make copy/paste from v4 maps dangerous.

Test signals: Probe IPA v5.0, validate channel/event setup with widened fields, read `HW_PARAM_2` and `HW_PARAM_4`, exercise low-latency/QoS configuration, command paths, doorbells, IRQ clear/mask, and sustained traffic.

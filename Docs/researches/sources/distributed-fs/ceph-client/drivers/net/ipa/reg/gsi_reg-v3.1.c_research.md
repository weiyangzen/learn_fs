# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v3.1.c

Purpose: Defines the GSI register descriptor table for GSI v1.0 as paired with IPA v3.1.

Important APIs and data: Exports `const struct regs gsi_regs_v3_1`. The file defines channel context, event context, doorbell, status, command, interrupt, error-log, and scratch registers using `REG*` macros. Field masks cover channel protocol/direction/EE/channel ID/event ring index/state/element size, channel ring length, QoS weight/prefetch/doorbell engine, event ring parameters, command opcodes, interrupt selection, error fields, and scratch fields.

Control flow and integration: There is no executable control flow. Runtime GSI code indexes `gsi_regs_v3_1.reg` through common helpers to program channels, event rings, doorbells, IRQ masks, and error handling for AP execution-environment offsets.

State and persistence: Static constant descriptors encode hardware offsets under the older `0x4000 * GSI_EE_AP` execution-environment window and `0x80` channel/event strides. Register values persist in hardware, not in this file.

Dependencies: Includes `gsi_reg.h`, `ipa_version.h`, and `reg.h`. It depends on enum register IDs and field IDs matching the array layout.

Risks: v3.1 lacks later hardware parameter descriptors such as `HW_PARAM_2`; code must gate feature discovery accordingly. Incorrect AP EE base offsets or field widths can break channel setup, event delivery, or interrupt clearing.

Test signals: Probe an IPA v3.1 platform, allocate channels/events, ring doorbells, receive IRQs, and decode error logs using the v3.1 map.

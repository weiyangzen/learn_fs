# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.5.c

Purpose: Defines the GSI register descriptor table for IPA v4.5 / GSI v2.5 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v4_5`. The map uses the newer v4 AP EE base offsets and retains channel context, event context, command, doorbell, interrupt, error, and scratch descriptors. QoS includes `PREFETCH_MODE` and `EMPTY_LVL_THRSHOLD`; `HW_PARAM_2` exposes SDMA, RD/WR-engine, inter-EE, pending-translate, and full-logic capabilities.

Control flow and integration: Selected by version-specific GSI register selection, then used by the shared GSI code for all MMIO offset and field operations.

State and persistence: Static metadata only. The hardware state written via this map includes channel/event ring configuration, interrupt state, doorbells, and error logs.

Dependencies: Depends on shared register/field IDs and the `REG_STRIDE_FIELDS` macros from `reg.h`.

Risks: Field availability differs from v4.9 and v4.11; code that assumes `DB_IN_BYTES` or `GENERIC_PARAMS` on v4.5 would encode nonexistent bits. Offsets must align with the shifted v4.5 register aperture.

Test signals: IPA v4.5 probe, capability reads, channel/event allocation, interrupt generation/clear, doorbell writes, and traffic over GSI channels.

# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v3.5.1.c

Purpose: Defines the GSI register descriptor table for GSI v1.3 / IPA v3.5.1-era hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v3_5_1`. It is structurally close to the v3.1 table but adds `HW_PARAM_2` field masks for channel pending translation, full-channel logic, and status-related hardware capability discovery. It retains legacy channel context, event context, QoS, doorbell, command, interrupt, error-log, and scratch descriptors.

Control flow and integration: Common GSI code selects this table for IPA v3.5.1 platforms and uses it for MMIO offsets and bitfield packing/unpacking. `HW_PARAM_2` lets setup code discover capabilities rather than relying only on fixed data.

State and persistence: The file contains only static descriptor state. It uses the same older AP EE window pattern and per-channel/per-event stride model as v3.1.

Dependencies: Depends on shared GSI register ID enums, field ID enums, execution-environment IDs, and the generic `reg` helpers.

Risks: This map is near-identical to adjacent versions, so copy/paste drift in a single field mask or offset is hard to spot. Consumers must not assume later SDMA or RD/WR-engine fields exist just because `HW_PARAM_2` is present.

Test signals: Hardware probe on IPA v3.5.1, capability reads from `HW_PARAM_2`, channel/event setup, command completion, IRQ mask/clear, and error-log decode.

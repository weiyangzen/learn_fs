# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/gsi_reg-v4.9.c

Purpose: Defines the GSI register descriptor table for IPA v4.9 / GSI v2.9 hardware.

Important APIs and data: Exports `const struct regs gsi_regs_v4_9`. It follows the v4.5-style base layout and adds QoS support for `DB_IN_BYTES` along with weighted round-robin, max prefetch, prefetch mode, and empty-level threshold fields. `HW_PARAM_2` includes SDMA and RD/WR/inter-EE capability fields.

Control flow and integration: Shared GSI setup uses this descriptor set for channel context programming, event ring setup, doorbells, commands, IRQ handling, and hardware capability discovery.

State and persistence: Only static descriptors live in the file. Hardware register values programmed through them remain active until reset or channel teardown.

Dependencies: Coupled to `gsi_reg.h` enum ordering and `reg.h` helper behavior.

Risks: This map is almost identical to v4.5/v4.11, so version-table selection must be precise. Enabling byte-based doorbell logic on versions that lack `DB_IN_BYTES`, or omitting it on v4.9 when required, can break ring updates.

Test signals: Probe v4.9 hardware, validate QoS programming including byte doorbells, exercise channel and event command paths, and confirm interrupts and error logs decode correctly.

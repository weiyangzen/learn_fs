# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.2.c

Purpose: Defines IPA core register descriptors for IPA v4.2 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_2`. It includes `FILT_ROUT_HASH_EN` and `FILT_ROUT_HASH_FLUSH` descriptors even though higher-level table logic treats IPA v4.2 as not supporting hashed tables. The map covers compatibility, clocks, route, shared memory, QSB, aggregation, IPA_BCR, counter/TX/flavor/idle, resource groups, endpoint setup/status, IRQ, UC IRQ, and suspend registers.

Control flow and integration: Common IPA code uses the map for MMIO access on v4.2 platforms. `ipa_table_hash_support()` special-cases this version, so table memory validation expects absent or zero-sized hashed table regions despite register descriptors existing.

State and persistence: Static register descriptors only. Hardware state persists in MMIO registers after programming.

Dependencies: Depends on `ipa_reg.h` ID definitions and version selection code. Endpoint and resource paths expect the v4.2 offsets and field widths.

Risks: The presence of hash enable/flush descriptors can mislead callers; feature policy must follow `ipa_table_hash_support()`. v4.2 differs from v4.5+ in timer/qtime availability and some endpoint/hash handling.

Test signals: Probe v4.2 with hashed table regions absent or zero-sized; verify table setup skips hashes; configure endpoints and resources; exercise IRQ/UC paths and traffic without hash-table use.

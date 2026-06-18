# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.7.c

Purpose: Defines IPA core register descriptors for IPA v4.7 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_7`. It follows the v4.5-family layout with compatibility, clock, route, shared memory, QSB, legacy hash flush, aggregation, local packet context, TX, flavor, idle, qtime/timer, resource group, endpoint, combined endpoint filter/router hash, and IRQ/UC/suspend descriptors.

Control flow and integration: Selected by hardware data for v4.7 platforms and used by common IPA setup, endpoint, resource, table, and interrupt code.

State and persistence: Contains only static descriptor state. Register values programmed through these descriptors persist in hardware.

Dependencies: Coupled to `ipa_reg.h` IDs and to feature paths that expect pre-v5 hash/cache layout.

Risks: The v4.7 file is close to v4.5/v4.9 and can be easy to interchange accidentally. Small field-mask differences in endpoint header extension, aggregation, or compatibility fields may only show up under specific offload/aggregation traffic.

Test signals: Probe v4.7, initialize endpoints, run TX/RX traffic with checksum/header/aggregation settings, flush hash tables, and verify IPA/UC/suspend IRQ handling.

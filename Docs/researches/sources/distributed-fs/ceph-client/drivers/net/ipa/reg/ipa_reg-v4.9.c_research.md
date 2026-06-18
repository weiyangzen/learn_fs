# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v4.9.c

Purpose: Defines IPA core register descriptors for IPA v4.9 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v4_9`. The map is in the v4.5/v4.7 family and includes expanded compatibility fields, route/shared memory/QSB, legacy hash flush, aggregation, local packet context, TX configuration, flavor, idle/qtime/timer registers, resource groups, endpoint setup/status, combined endpoint filter/router hash config, and IRQ/UC/suspend descriptors.

Control flow and integration: Common IPA code uses this descriptor set for all v4.9 MMIO accesses. Table code uses its legacy hash flush and combined endpoint hash register fields.

State and persistence: Static register metadata only. Hardware state written via these descriptors remains active until reset or explicit reconfiguration.

Dependencies: Depends on `ipa_reg.h` ID/field ordering and `ipa_version.h` version dispatch.

Risks: v4.9 is pre-v5 despite being close to the v5 boundary; cache flush remains `FILT_ROUT_HASH_FLUSH`, and filter/router hash tuple configuration remains combined. Version-boundary mistakes will affect table cache coherency and endpoint hash programming.

Test signals: Probe v4.9, validate hash flush after table changes, configure endpoints/resources/timers, exercise interrupts, and run traffic through aggregation and checksum/header offload paths.

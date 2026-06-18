# sources/distributed-fs/ceph-client/drivers/net/ipa/reg/ipa_reg-v3.1.c

Purpose: Defines IPA core register descriptors for IPA v3.1 hardware.

Important APIs and data: Exports `const struct regs ipa_regs_v3_1`. The map covers compatibility/configuration, clock-on status, default routing, shared memory size, QSB read/write limits, legacy filter/route hash flush, aggregation state/force-close, IPA_BCR, local packet processor context, counter configuration, source/destination resource groups 0-7, endpoint init/status/hash configuration, IPA IRQ registers, microcontroller IRQ, and suspend IRQ registers.

Control flow and integration: Runtime IPA code selects this descriptor table by hardware version, then uses `ipa_reg()` and generic register helpers to encode fields and compute MMIO offsets for setup, endpoint configuration, table hash flushing, interrupts, and resource programming.

State and persistence: Static constant descriptors only. Hardware state programmed through these offsets persists until reset or reconfiguration.

Dependencies: Depends on `ipa_reg.h` register and field IDs plus `ipa_version.h`. The file uses legacy pre-v5 endpoint stride and hash-combined register layout.

Risks: v3.1 has older bit positions for routing, clocks, resource limits, and endpoint hash fields. Global-filter bitmap behavior in table code also applies to this generation. Misusing later v4/v5 maps would program wrong offsets or fields.

Test signals: IPA v3.1 probe, endpoint configuration, resource limit programming, table hash flush, IRQ handling, microcontroller interrupt delivery, and aggregation force-close behavior.

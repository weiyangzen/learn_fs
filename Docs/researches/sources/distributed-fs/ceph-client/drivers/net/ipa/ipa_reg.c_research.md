# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_reg.c

Purpose: selects the correct IPA register table for a hardware version, validates register IDs against version support, maps the `"ipa-reg"` MMIO resource, and exposes register metadata lookup.

Important APIs/functions: `ipa_reg()` warns on invalid register use for the active version and returns `reg(ipa->regs, reg_id)`. `ipa_reg_init()` resolves `ipa_regs_*` table by version, checks table size, maps the platform memory resource named `"ipa-reg"`, and stores `ipa->regs`/`reg_virt`. `ipa_reg_exit()` unmaps MMIO.

Control flow: probe sets `ipa->version` from match data, then calls `ipa_reg_init()`. All hardware configuration code later calls `ipa_reg()` before register offsets/field encodings. Version validation whitelists base registers and conditionally allows hash/cache, BCR/counter, Qtime timers, resource group, endpoint control/cache, and suspend-clear registers.

State/persistence: `ipa->regs` and `ipa->reg_virt` persist from init until exit. No register values are cached here.

Dependencies/integration: depends on generated/static `ipa_regs_v*` tables declared in `ipa_reg.h`, platform resources, `ioremap`, and common `reg.h` helpers used by all IPA modules.

Risks: incomplete or overly permissive version validation can allow invalid MMIO accesses or block legitimate registers. The v5.2 path reuses v5.0 register metadata. Any caller that ignores a NULL `ipa_reg()` result can fault after a warning.

Test signals: probe maps `"ipa-reg"`, all supported compatibles select a non-NULL register table, register validation warnings are absent in normal boot, and deconfig unmaps once.

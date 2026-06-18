# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_reg.h

Purpose: defines the register ID namespace, per-register field IDs, hardware enum values, IPA IRQ IDs, extern register tables, and register lifecycle APIs.

Important APIs/types: `enum ipa_reg_id` lists global, resource, endpoint, and IRQ registers. Field enums cover `COMP_CFG`, `CLKON_CFG`, route/default pipe, shared memory, QSB limits, hash/cache, timers, resource groups, endpoint configuration, status, and IRQ microcontroller fields. Hardware value enums define checksum offload, NAT type, endpoint mode, aggregation enable/type, sequencer types, pulse granularities, and IPA IRQ bit positions. `ipa_reg()`, `ipa_reg_init()`, and `ipa_reg_exit()` are the public lookup/lifecycle APIs.

Control flow: modules use `ipa_reg()` plus `reg_offset`, `reg_n_offset`, `reg_encode`, `reg_decode`, and `reg_bit` to avoid open-coded bit masks. Parameterized registers use per-endpoint, per-resource, or per-unit offsets through register metadata.

State/persistence: no mutable state is stored in the header, but enum values are cross-module contracts and sometimes hardware ABI values.

Dependencies/integration: includes common `reg.h`; register tables are version-specific and selected by `ipa_reg.c`. Endpoint, main, memory, interrupt, resource, table, UC, and command code all depend on these IDs.

Risks: enum ordering/indexing must match field-mask arrays in `ipa_regs_v*`. Hardware value enums must not be renumbered. Version comments are documentation only; runtime validity is enforced in `ipa_reg.c`.

Test signals: all field IDs used by code are present in the selected register table, boot logs have no invalid register warnings, and register programming produces expected hardware behavior across supported IPA versions.

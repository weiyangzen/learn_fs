# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_table.h

Purpose: Declares the IPA filter and route table lifecycle API used by probe, configuration, modem/AP reset, and rule synchronization code.

Important APIs and types: The header forward-declares `struct ipa` and exposes `ipa_filtered_valid()`, `ipa_table_hash_support()`, `ipa_table_reset()`, `ipa_table_hash_flush()`, `ipa_table_setup()`, `ipa_table_config()`, `ipa_table_init()`, `ipa_table_exit()`, and `ipa_table_mem_valid()`. The API is intentionally table-centric and hides DMA allocation, IPA memory-region lookup, and command construction inside `ipa_table.c`.

Control flow and integration: Callers validate table memory and filtering endpoint masks before table initialization, call `ipa_table_init()` to allocate coherent backing memory, call `ipa_table_setup()` and `ipa_table_config()` during hardware setup, call `ipa_table_reset()` when resetting AP or modem-owned entries, and call `ipa_table_hash_flush()` after hashed rule updates. There is no matching deconfig/teardown for setup/config because hardware state is overwritten or lost as part of broader IPA teardown.

State and persistence: The header owns no state, but its functions allocate and release `ipa->table_virt`/`ipa->table_addr` and program persistent hardware table/cache state.

Dependencies: Requires Linux integer types and the full IPA core definition at implementation call sites. It is coupled to `ipa_mem`, `ipa_cmd`, endpoint, version, and register code through the implementation.

Risks: Prototype drift can break setup/reset ordering across the IPA driver. The boolean parameters (`modem`, `filter`) are compact but easy to misuse, so call sites should be checked for ownership semantics. Hash support is version-derived rather than platform-data-derived, so new hardware versions must update version logic.

Test signals: Build coverage across IPA probe/remove and reset paths; runtime coverage of table setup, hash flush, and modem/AP reset paths on hash-capable and non-hash-capable versions.

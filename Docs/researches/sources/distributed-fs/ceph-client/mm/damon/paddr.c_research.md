# sources/distributed-fs/ceph-client/mm/damon/paddr.c

Purpose: Registers DAMON operations for monitoring and acting on physical address ranges.

Important APIs, types, and functions: Address conversion helpers map DAMON core addresses through `ctx->addr_unit`. `damon_pa_prepare_access_checks()` samples a random address per region and marks its folio old. `damon_pa_check_accesses()` checks if sampled folios became young and updates access rates. DAMOS action handlers implement `DAMOS_PAGEOUT`, `DAMOS_LRU_PRIO`, `DAMOS_LRU_DEPRIO`, `DAMOS_MIGRATE_HOT`, `DAMOS_MIGRATE_COLD`, and `DAMOS_STAT`. `damon_pa_scheme_score()` selects hot/cold scoring. `damon_pa_initcall()` registers `DAMON_OPS_PADDR`.

Control flow: Monitoring periodically marks sample folios old, sleeps in core, then checks young/idle state. Scheme application iterates physical pages/folios in a region, applies ops filters, then reclaims, activates, deactivates, migrates, or only counts filter-passed size. Pageout automatically installs a young filter unless one already exists.

State and persistence: Uses only runtime DAMON regions and scheme fields. `s->last_applied` avoids reapplying to the same folio during region walks. Paddr ops mutate LRU isolation, folio active state, reference/young bits, and reclaim/migration outcomes.

Dependencies and integration: Depends on `ops-common` folio helpers, reclaim, LRU, migration, memory tiers, page idle, and DAMON core operation registration.

Risks: Physical address iteration must account for large folio sizes and invalid PFNs. The static cache in `__damon_pa_check_access()` reuses last folio results across regions, which improves performance but must remain correct with address-unit conversion. Action handlers can be costly over large regions and depend on filter semantics.

Test signals: DAMON paddr monitoring over system RAM, pageout effects, LRU activation/deactivation stats, NUMA migration actions, young-filter behavior, and registration failure when duplicate ops IDs are used.

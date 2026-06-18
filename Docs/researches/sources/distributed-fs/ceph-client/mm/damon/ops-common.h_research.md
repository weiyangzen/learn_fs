# sources/distributed-fs/ceph-client/mm/damon/ops-common.h

Purpose: Declares shared DAMON operations helpers for address backends.

Important APIs: Declares folio lookup and aging helpers (`damon_get_folio()`, `damon_ptep_mkold()`, `damon_pmdp_mkold()`, `damon_folio_mkold()`, `damon_folio_young()`), score helpers (`damon_cold_score()`, `damon_hot_score()`), filter/migration helpers (`damos_folio_filter_match()`, `damon_migrate_pages()`), and `damos_ops_has_filter()`.

Control flow: Header-only control is limited to providing prototypes; consumers include paddr/vaddr operation implementations and rely on `ops-common.o` being built.

State and persistence: No state.

Dependencies and integration: Includes `linux/damon.h`; Kbuild adds `ops-common.o` when vaddr or paddr ops are enabled.

Risks: Prototype drift against implementation or `linux/damon.h` type changes will break backends. Adding helpers requires Kbuild dependency checks for all consumers.

Test signals: Compile paddr/vaddr combinations and run DAMON operation tests that exercise declared helper paths.

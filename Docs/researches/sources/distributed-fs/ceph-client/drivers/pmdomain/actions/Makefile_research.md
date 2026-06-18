# sources/distributed-fs/ceph-client/drivers/pmdomain/actions/Makefile

Purpose: maps Actions Owl PM-domain Kconfig symbols to Kbuild objects.

Important APIs/types/functions: `CONFIG_OWL_PM_DOMAINS_HELPER` builds `owl-sps-helper.o`; `CONFIG_OWL_PM_DOMAINS` builds `owl-sps.o`.

Control flow: none at runtime.

State and persistence: build outputs reflect `.config`.

Dependencies/integration: synchronized with `actions/Kconfig`; `owl-sps.o` calls the helper exported by `owl-sps-helper.o`.

Risks: omitting the helper object would break `owl_sps_set_pg()` linkage; stale names make selected symbols unbuildable.

Test signals: build with helper only and with full `OWL_PM_DOMAINS`, including modular/allbuilt configurations if allowed by the tree.

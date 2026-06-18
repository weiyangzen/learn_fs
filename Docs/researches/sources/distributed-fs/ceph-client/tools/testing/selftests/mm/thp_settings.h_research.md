# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thp_settings.h

Purpose: declares the shared transparent hugepage settings model and helper API used by mm selftests that need to inspect or temporarily modify THP policy.

Important APIs and types: enums model anon THP policy, defrag policy, and shmem policy. Structs include `hugepages_settings`, `khugepaged_settings`, `shmem_hugepages_settings`, and aggregate `thp_settings` with per-order arrays sized by `NR_ORDERS`.

Control flow and state: no executable flow; consumers include this header and link `thp_settings.c` to call read/write/save/restore/stack APIs and supported-order queries. The header defines data shapes and prototypes only.

Dependencies and risks: depends on standard bool/size/integer headers. Enum ordering must remain aligned with string arrays in `thp_settings.c` and sysfs accepted values; `NR_ORDERS` bounds represented page-size orders.

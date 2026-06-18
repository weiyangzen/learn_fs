<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink.h -->
# sources/distributed-fs/ceph-client/kernel/power/em_netlink.h

Purpose: Declares the Energy Model core functions used by netlink support and provides no-op stubs when Energy Model netlink support is not compiled.

Important APIs/types/functions: `for_each_em_perf_domain()`, `em_perf_domain_get_by_id()`, `em_notify_pd_created()`, `em_notify_pd_deleted()`, and `em_notify_pd_updated()`.

Control flow: Under `CONFIG_ENERGY_MODEL && CONFIG_NET`, declarations are provided for the real implementations. Otherwise iteration returns `-EINVAL`, lookup returns `NULL`, and notification helpers do nothing.

State and persistence: No state. It defines the compile-time contract between `energy_model.c` and optional netlink files.

Dependencies/integration: Depends on `struct em_perf_domain` from Energy Model headers and mirrors `kernel/power/Makefile`, where netlink files are included in `em.o` only with `CONFIG_NET`.

Risks: The config condition must stay aligned with build rules; otherwise callers may link against missing real symbols or silently use stubs. Stub return values should be acceptable to callers in non-net builds.

Test signals: Build with Energy Model plus NET, Energy Model without NET, and without Energy Model; confirm notifications compile out and lookup/iteration users handle stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink.c -->
# sources/distributed-fs/ceph-client/kernel/power/em_netlink.c

Purpose: Exposes Energy Model performance domains and performance tables through generic netlink and emits multicast events when performance domains are created, updated, or deleted.

Important APIs/types/functions: netlink command handlers `dev_energymodel_nl_get_perf_domains_doit()`, `dev_energymodel_nl_get_perf_domains_dumpit()`, `dev_energymodel_nl_get_perf_table_doit()`, notifications `em_notify_pd_created()`, `em_notify_pd_updated()`, `em_notify_pd_deleted()`, and init `em_netlink_init()`. Helpers include `__em_nl_get_pd_size()`, `__em_nl_get_pd()`, `__em_nl_get_pd_table_size()`, `__em_nl_get_pd_table()`, and `__em_notify_pd_table()`.

Control flow: The get-domain doit path validates a performance domain id attribute, looks up the domain by id, sizes a reply, emits id/flags/cpu attributes, and replies. The dump path iterates `for_each_em_perf_domain()` and emits one generic-netlink message per domain after the starting index. The get-table path resolves the domain id, sizes for all perf states, reads the current RCU-protected EM table, and nests state attributes for performance, frequency, power, cost, and flags. Notifications first check multicast listeners, build the same table message for create/update or id-only delete message, and multicast on the event group.

State and persistence: The file owns no EM state; it serializes snapshots from `struct em_perf_domain` and RCU-protected perf tables. Generic netlink family state is generated in `em_netlink_autogen.c` and registered at postcore init.

Dependencies/integration: Depends on Energy Model core lookup/iteration from `energy_model.c`, generic netlink, UAPI `dev_energymodel.h`, init net namespace listeners, RCU table reads, and generated YNL family definitions.

Risks: `dev_energymodel_nl_get_perf_domains_dumpit()` reads `cb->args[0]` as a start index but does not update it after emitting domains, which is a concrete risk for multipart dump progress/repetition if the skb fills. Several error paths call `genlmsg_cancel()` or free skb after partial construction; header/nest handling must remain exact. Perf domain lookup returns pointers protected by the EM list mutex only during lookup/iteration; deletion races rely on higher-level EM lifetime behavior and netlink notification ordering.

Test signals: netlink doit for valid/invalid domain ids, dump across more domains than fit in one skb, table reads while EM updates replace the RCU table, listener/no-listener notification paths, create/update/delete event contents, policy validation, and kernel netlink selftests generated from `dev-energymodel.yaml`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.c -->
# sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.c

Purpose: Auto-generated YNL generic-netlink family implementation for the device Energy Model UAPI.

Important APIs/types/functions: Defines policies `dev_energymodel_get_perf_domains_nl_policy[]` and `dev_energymodel_get_perf_table_nl_policy[]`, split ops `dev_energymodel_nl_ops[]`, multicast groups `dev_energymodel_nl_mcgrps[]`, and exported family object `dev_energymodel_nl_family`.

Control flow: The ops table wires `DEV_ENERGYMODEL_CMD_GET_PERF_DOMAINS` to both doit and dump handlers and `DEV_ENERGYMODEL_CMD_GET_PERF_TABLE` to its doit handler. Policies constrain requested domain id attributes to `NLA_U32`. The family is netns-aware, uses parallel ops, and points to the generated multicast event group.

State and persistence: The generated `genl_family` is `__ro_after_init`; after registration it is the persistent kernel representation of the netlink family until shutdown.

Dependencies/integration: Generated from `Documentation/netlink/specs/dev-energymodel.yaml`; includes generic netlink headers, `em_netlink_autogen.h`, and UAPI `linux/dev_energymodel.h`. Runtime handlers live in `em_netlink.c`.

Risks: Manual edits would be overwritten by YNL regeneration. Policy maxattr values must match UAPI enum definitions. `parallel_ops = true` means handlers must be safe under concurrent netlink requests.

Test signals: Regenerate from YAML and compare, netlink policy validation for missing/wrong attrs, family registration, parallel requests, and multicast group presence in netlink introspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.c -->

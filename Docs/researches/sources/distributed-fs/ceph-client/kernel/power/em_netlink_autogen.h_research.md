<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.h -->
# sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.h

Purpose: Auto-generated header declaring Energy Model generic-netlink handlers, multicast group ids, and the family object.

Important APIs/types/functions: Declarations for `dev_energymodel_nl_get_perf_domains_doit()`, `dev_energymodel_nl_get_perf_domains_dumpit()`, `dev_energymodel_nl_get_perf_table_doit()`, enum `DEV_ENERGYMODEL_NLGRP_EVENT`, and `extern struct genl_family dev_energymodel_nl_family`.

Control flow: No executable logic; it provides compile-time prototypes consumed by the generated family and the hand-written netlink encoder.

State and persistence: No state in the header. The declared family state is defined in `em_netlink_autogen.c`.

Dependencies/integration: Generated from `Documentation/netlink/specs/dev-energymodel.yaml`; includes netlink/genetlink and UAPI Energy Model headers.

Risks: Must not drift from the generated C file or UAPI enums. Since it declares command handlers implemented manually, signature changes in YNL generation require matching code changes in `em_netlink.c`.

Test signals: Full build after YNL regeneration, sparse/header self-containment checks, and netlink family registration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/power/em_netlink_autogen.h -->

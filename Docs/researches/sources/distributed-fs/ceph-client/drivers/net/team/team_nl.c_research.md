# sources/distributed-fs/ceph-client/drivers/net/team/team_nl.c

Purpose: generated generic-netlink policy and operation table for the team UAPI described by `Documentation/netlink/specs/team.yaml`.

Important APIs/functions: defines `team_attr_option_nl_policy`, `team_item_option_nl_policy`, `team_nl_policy`, and `team_nl_ops`. The ops table binds `TEAM_CMD_NOOP`, `TEAM_CMD_OPTIONS_SET`, `TEAM_CMD_OPTIONS_GET`, and `TEAM_CMD_PORT_LIST_GET` to handler functions implemented in `team_core.c`.

Control flow: generic-netlink family registration in `team_core.c` references these policy and op arrays. Incoming messages are validated with non-strict legacy validation and dispatched to the corresponding `doit` handler; mutating/get/list commands require `GENL_ADMIN_PERM` except NOOP.

State and persistence: static const policy/ops tables only; no mutable state.

Dependencies and integration: includes netlink/genetlink headers, `team_nl.h`, and UAPI `linux/if_team.h`. Must stay synchronized with the YAML spec and the handler prototypes.

Risks: file is generated and marked "Do not edit directly"; manual edits may be overwritten or diverge from UAPI. Non-strict validation preserves compatibility but shifts deeper validation to handlers.

Test signals: regenerate from YAML and diff; run generic-netlink commands for noop, options get/set, and port list get; verify permission checks and malformed nested attributes are rejected by policy or core handler validation.

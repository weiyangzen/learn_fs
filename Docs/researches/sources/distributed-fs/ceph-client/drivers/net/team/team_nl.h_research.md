# sources/distributed-fs/ceph-client/drivers/net/team/team_nl.h

Purpose: generated header exposing the team generic-netlink policy arrays, ops table, and handler prototypes to `team_core.c` and `team_nl.c`.

Important APIs/types/functions: declares `team_attr_option_nl_policy`, `team_item_option_nl_policy`, `team_nl_policy`, `team_nl_ops[4]`, and the four handler prototypes `team_nl_noop_doit`, `team_nl_options_set_doit`, `team_nl_options_get_doit`, and `team_nl_port_list_get_doit`.

Control flow: no executable flow. It provides compile-time linkage between generated netlink tables and core handler implementations.

State and persistence: no mutable state; extern declarations only.

Dependencies and integration: includes netlink/genetlink headers and UAPI `linux/if_team.h`. Generated from `Documentation/netlink/specs/team.yaml`.

Risks: prototype or array-size drift between this header, generated `team_nl.c`, and `team_core.c` will break build or dispatch. Manual edits are discouraged by the generated-file notice.

Test signals: full build of `team.o`; YNL regeneration diff; compile failures for handler signature changes.

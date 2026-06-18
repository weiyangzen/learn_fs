
# sources/distributed-fs/ceph-client/include/uapi/linux/if_team.h

## Purpose

`if_team.h` is an auto-generated YNL UAPI header for the team generic-netlink family. It defines family metadata, string limits, multicast group name, attributes, nested option/port entries, and commands. The complete 79-line file was read.

## Important APIs, Types, and Functions

Constants include `TEAM_GENL_NAME`, `TEAM_GENL_VERSION`, `TEAM_STRING_MAX_LEN`, and `TEAM_GENL_CHANGE_EVENT_MC_GRP_NAME`. Enums define `TEAM_ATTR_*`, `TEAM_ATTR_ITEM_OPTION_*`, `TEAM_ATTR_OPTION_*`, `TEAM_ATTR_ITEM_PORT_*`, `TEAM_ATTR_PORT_*`, and commands `TEAM_CMD_NOOP`, `TEAM_CMD_OPTIONS_SET`, `TEAM_CMD_OPTIONS_GET`, and `TEAM_CMD_PORT_LIST_GET`.

## Control Flow

No executable flow exists. Generic-netlink requests set or get team options and list ports. Kernel team code emits change events on the configured multicast group.

## State and Persistence Behavior

Team device state, options, and port membership live in kernel team objects. The header only fixes the netlink contract used to mutate and observe that state.

## Dependencies and Integration Points

It is generated from `Documentation/netlink/specs/team.yaml` and integrates with the YNL tooling, generic netlink, the team driver, and users such as teamd/libteam.

## Risks and Edge Cases

Manual edits can be overwritten or diverge from the YAML spec. Risks include attribute renumbering, inconsistent nested list shapes, string-length assumptions, and stale users expecting old option type/data encoding.

## Test Signals

Regeneration diff checks, generic-netlink policy tests, team option set/get tests, port-list dump tests, and multicast change-event tests.

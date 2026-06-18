# sources/distributed-fs/ceph-client/Documentation/netlink/specs/team.yaml

Purpose: this generic-netlink legacy schema documents the network team driver family, covering option management, port listing, and change-event integration.

Important APIs, types, and functions: family metadata points to `team-genl-name`, `team-genl-version`, global kernel policy, and `linux/if_team.h`. Constants include string max length 32 and multicast group name `change_event`. The top-level `team` attribute set contains `team-ifindex`, nested option list, and nested port list. Option list entries nest `attr-option` fields: option name, changed/removed flags, type, raw data, per-port ifindex, and array index. Port list entries nest `attr-port`: ifindex, changed/linkup/removed flags, speed, and duplex.

Control flow: `noop` value 0 returns the family/team ifindex. `options-set` is admin-only and sends `team-ifindex` plus option list, with an echo-like reply. `options-get` is admin-only and fetches options for a team ifindex. `port-list-get` is admin-only and fetches port information.

State and persistence: team device state, options, and ports are owned by the team driver and persist while the team interface exists. The schema documents change flags but does not implement storage.

Dependencies and integration: depends on the generic netlink legacy team family, team kernel driver, `linux/if_team.h`, and userspace team management daemons/tools.

Risks: option `data` is binary and typed by a separate `type` field, so consumers must decode per option. `dont-validate: strict` indicates legacy messages may not pass modern strict policy. Test signals include option get/set round trips on a team device, nested list parsing, per-port option handling, port list dump, and change-event notification monitoring.

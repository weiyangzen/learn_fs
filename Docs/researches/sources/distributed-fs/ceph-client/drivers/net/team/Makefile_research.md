# sources/distributed-fs/ceph-client/drivers/net/team/Makefile

Purpose: builds the team core composite object and optional team mode modules.

Important APIs/types/functions: `team-y := team_core.o team_nl.o` links generated netlink glue with the core implementation. `obj-$(CONFIG_NET_TEAM)` builds `team.o`. Each `CONFIG_NET_TEAM_MODE_*` builds a standalone `team_mode_*.o` module/object.

Control flow: Kbuild includes objects according to Kconfig tristate values. Core and generated netlink code are inseparable within `team.o`; modes remain independently loadable providers registered with `team_mode_register`.

State and persistence: no runtime state; build graph only.

Dependencies and integration: depends on Kbuild and the Kconfig symbols from `team/Kconfig`. Mode modules integrate with the core through exported symbols from `team_core.c`.

Risks: omitting `team_nl.o` from `team-y` would break generic-netlink family registration. Mode objects built without matching aliases would not autoload for mode changes.

Test signals: inspect `modules.order` or built-in objects for selected configs; load `team` and each mode module; run `modinfo` to confirm aliases such as `team-mode-broadcast`.

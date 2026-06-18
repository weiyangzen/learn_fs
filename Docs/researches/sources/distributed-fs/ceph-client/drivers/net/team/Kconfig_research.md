# sources/distributed-fs/ceph-client/drivers/net/team/Kconfig

Purpose: declares Kconfig options for the Ethernet team driver and its selectable transmit modes.

Important APIs/types/functions: `NET_TEAM` is a tristate menuconfig for the core `team` module. Mode options are `NET_TEAM_MODE_BROADCAST`, `NET_TEAM_MODE_ROUNDROBIN`, `NET_TEAM_MODE_RANDOM`, `NET_TEAM_MODE_ACTIVEBACKUP`, and `NET_TEAM_MODE_LOADBALANCE`, each depending on `NET_TEAM` and mapping to its own module.

Control flow: build-time selection controls whether the core team driver and optional mode modules are compiled built-in, as modules, or omitted. Help text documents `ip link add ... type team` for core device creation and describes each mode's selection behavior.

State and persistence: no runtime state. Configuration persists in the kernel build config and controls module availability/autoloading.

Dependencies and integration: integrates with the drivers/net Kconfig tree and the Makefile in the same directory. Runtime mode autoload relies on module aliases from the corresponding `team_mode_*.c` files.

Risks: load-balance mode depends on userspace-supplied BPF hash configuration, while active-backup deliberately does not rewrite port MACs and pushes that responsibility to userspace. Building the core without needed mode modules leaves `team_change_mode` unable to find those modes unless modules can be requested.

Test signals: build all y/m/n combinations that make sense, verify generated modules exist, and confirm `request_module("team-mode-%s")` can load each mode selected as module.

# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_torture.sh

Purpose: Stress-tests dynamic netconsole target lifetime and transmit paths under concurrent reconfiguration. It repeatedly writes kernel log messages while enabling/disabling the primary configfs target, creating/removing extra dynamic targets, and flapping the source interface.

Important APIs/functions: Uses `lib_netcons.sh` for `check_for_dependencies`, `set_network`, `create_dynamic_target`, `_create_dynamic_target`, and `cleanup`. Local helpers are `create_and_delete_random_target`, `toggle_netcons_target`, and `toggle_iface`. Kernel integration is through `/dev/kmsg`, `/proc/sys/kernel/printk`, configfs under `NETCONS_CONFIGFS`, `ip link`, and `modprobe netconsole/netdevsim`.

Control flow: The script fixes extended IPv6 mode, prepares a namespace/interface topology, creates one target, then loops `ITERATIONS` times writing ten messages per iteration. Every 30/50/70 iterations it starts a background target toggle, random target churn, or interface down/up job. A final `wait` synchronizes all background work before returning `EXIT_STATUS`.

State and persistence: State is transient kernel configfs directories, printk level, namespaces, and netdevsim links. The `trap cleanup EXIT` path is the persistence boundary and should remove dynamic targets and network setup.

Dependencies and integration: Requires root, configfs netconsole dynamic support, netdevsim, netconsole, `iproute2`, and the netconsole shell library. It is most valuable with LOCKDEP, KASAN, and kmemleak enabled because success is mainly absence of kernel diagnostics.

Risks: Races are intentional; writes to `enabled` can fail under lock contention and are tolerated. `mktemp -u` has a small name collision risk, partly checked before use. Failures may appear as kernel warnings rather than shell errors.

Test signals: PASS is clean completion with no lockdep/KASAN/kmemleak reports, no leaked configfs targets, no stuck namespace/device state, and successful concurrent message emission under target churn.

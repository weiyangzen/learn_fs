<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_resume.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_resume.sh

Purpose: validates that cmdline netconsole targets disabled by source/destination interface disappearance automatically resume when netdevsim interfaces return.

Important functions/APIs: local `cleanup`, `trigger_deactivation`, `trigger_reactivation`; helper calls `cleanup_netcons`, `do_cleanup`, `check_netconsole_module`, `set_network`, `create_cmdline_str`, `wait_target_state`, `listen_port_and_save_to`, `wait_local_port_listen`, and `validate_msg`.

Control flow: for ifname and MAC binding modes, creates network, loads netconsole cmdline target, exposes `cmdline0` in configfs, waits for enabled state, unloads netdevsim to force disabled state, reloads netdevsim and restores MACs/names as needed, waits for enabled state, then captures a `/dev/kmsg` message.

State/dependencies: netconsole/netdevsim module lifecycle, configfs cmdline target, saved MAC addresses, namespace and interfaces. Risks include module unload side effects, race in device recreation, MAC-bound rename behavior, and cleanup invoked inside loop plus trap. Test signals are target state transitions and successful message capture in both bind modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_resume.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_cmdline.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_cmdline.sh

Purpose: verifies netconsole module parameter parsing and cmdline target initialization for interface-name and MAC binding modes.

Important functions/APIs: sources `lib_netcons.sh`; uses `check_netconsole_module`, `set_network`, `create_cmdline_str`, `listen_port_and_save_to`, `wait_local_port_listen`, `validate_msg`, `pkill_socat`, `do_cleanup`, `modprobe netconsole "$CMDLINE"`, and `rmmod netconsole`.

Control flow: unloads netconsole, sets up network once, then for each bind mode loads netconsole with constructed parameters, listens for UDP output, writes to `/dev/kmsg`, waits for capture, validates message, kills socat, unloads module, and repeats.

State/dependencies: netconsole module lifecycle, netdevsim network, printk level, namespace, `/tmp` captures. Risks include module unload blocked by existing users, no dynamic configfs cleanup for cmdline mode, and missing busywait failure check before validation. Test signals are message capture and validation for both bind modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_cmdline.sh -->

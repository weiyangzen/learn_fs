<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_basic.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_basic.sh

Purpose: basic dynamic netconsole delivery test over IPv4 and IPv6, in both basic and extended output formats.

Important functions/APIs: sources `lib_netcons.sh`; uses `check_for_dependencies`, `set_network`, `create_dynamic_target`, optional `set_user_data`, `listen_port_and_save_to`, `wait_for_port`, `validate_result`, `pkill_socat`, and `cleanup`. Loads `netdevsim` and `netconsole`.

Control flow: loops over `FORMAT=basic/extended` and `IP_VERSION=ipv6/ipv4`, configures printk levels, creates namespace and simulated interfaces, creates dynamic target, listens with socat, writes a message to `/dev/kmsg`, waits for output file, validates received message, and cleans up before next iteration.

State/dependencies: modules, net namespace, netdevsim interfaces, configfs target, `/tmp/$TARGET`, printk level, and socat process. Risks include polluting dmesg, leftover namespace/targets, timing waiting for UDP delivery, and shared `/tmp` filename collisions. Test signals are non-empty output file and format-specific validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_basic.sh -->

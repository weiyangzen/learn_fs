
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/lib/sh/lib_netcons.sh`

## Purpose
Shared shell library for netconsole selftests. It creates netdevsim-backed source/destination interfaces, configures netconsole dynamic targets, starts listeners, validates received console messages and userdata, and cleans up namespaces/devices.

## Important APIs, Types, And Functions
- Top-level variables define default IPv4/IPv6 addresses, UDP port, message text, configfs paths, namespace, and random netdevsim IDs.
- `set_network()`, `create_ifaces()`, `link_ifaces()`, and `configure_ip()` build a two-interface netdevsim topology with the destination in a namespace.
- `_create_dynamic_target()`, `create_dynamic_target()`, `create_cmdline_str()`, and `disable_release_append()` configure netconsole targets.
- `listen_port_and_save_to()`, `validate_msg()`, and `validate_result()` capture and validate netconsole output.
- `check_for_dependencies()`, `check_netconsole_module()`, `wait_target_state()`, `wait_for_port()`, and cleanup helpers provide test scaffolding.

## Control Flow
Tests source this file, call dependency checks, set up networking, create a configfs target or command-line target, start `socat` listeners inside the namespace, trigger console messages, validate output, then call cleanup through traps.

## State And Persistence
Creates netdevsim devices, network namespaces, configfs netconsole targets, user data directories, printk configuration changes, optional bonding netdevsim devices, and listener processes. Cleanup removes configfs entries, netdevsim devices, namespaces, and restores printk values.

## Dependencies And Integration Points
Depends on `net/lib.sh`, root privileges, `socat`, `ip`, `udevadm`, IPv6 support, netdevsim sysfs, and `NETCONSOLE_DYNAMIC` configfs. It also integrates with ksft exit status variables from the common shell library.

## Risks
Uses global variable state heavily and random netdevsim IDs. Several cleanup paths intentionally ignore failures to handle partial setup. Configfs target deletion must disable the target and remove userdata before `rmdir`.

## Test Signals
Validation checks that a listener output file is created, contains the expected message, and for extended format contains configured userdata. Dependency failures produce ksft skip exits.

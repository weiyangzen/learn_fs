# sources/distributed-fs/ceph-client/tools/testing/selftests/net/busy_poll_test.sh

Purpose: Tests busy-poll socket receive behavior over linked `netdevsim` devices, including suspend timeout and threaded NAPI mode.

Important APIs/types/functions: Uses `netdevsim` sysfs (`new_device`, `del_device`, `link_device`, `unlink_device`), namespaces, `busy_poller` generated helper, `socat`, `md5sum`, NAPI/busy-poll parameters, and `wait_local_port_listen`.

Control flow: The script loads `netdevsim`, creates two simulated devices, moves them into server/client namespaces, assigns IP addresses, opens namespace fds and gets ifindexes, links the simulated devices through sysfs, then runs three tests. Each `test_busypoll()` creates random data, starts `busy_poller` server with configured busy-poll/suspend/threaded options, sends data via `socat`, waits for completion, and compares input/output MD5 sums. It unlinks/deletes devices and removes namespaces/module at the end.

State and persistence behavior: Creates netdevsim devices, sysfs link state, namespaces, namespace file descriptors, temp data files, and a loaded kernel module. Cleanup paths remove namespaces and module, though early failures perform partial cleanup.

Dependencies and integration points: Requires root, `netdevsim`, generated `busy_poller` binary from YNL build, `socat`, `md5sum`, `udevadm`, and sysfs netdevsim control files.

Risks: No global trap covers all failures; early exits may leave netdevsim devices or module loaded. Random ID selection can collide. `modprobe -r netdevsim` can fail if devices remain. Data transfer uses 30-second timeout.

Test signals: All three transfer MD5 comparisons passing and exit 0 validate ordinary busy poll, busy poll with suspend, and threaded NAPI busy-poll mode.

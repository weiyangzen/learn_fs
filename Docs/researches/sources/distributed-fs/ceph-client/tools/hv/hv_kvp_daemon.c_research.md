# sources/distributed-fs/ceph-client/tools/hv/hv_kvp_daemon.c

## Purpose

`hv_kvp_daemon.c` is the Linux user-space Hyper-V Key Value Pair daemon. It registers with the kernel driver through `/dev/vmbus/hv_kvp`, services host requests, persists guest/host KVP pools, reports auto-generated guest facts such as OS version and IP addresses, and applies host-provided network configuration through a distribution-specific helper script.

## Important APIs, Types, and Functions

The file uses Hyper-V ABI structures and constants from `<linux/hyperv.h>`, especially `struct hv_kvp_msg`, `struct hv_kvp_ipaddr_value`, `KVP_OP_*`, `KVP_POOL_*`, and `HV_*` status codes. Local storage is modeled with `struct kvp_record` and `struct kvp_file_state`; `kvp_file_info[KVP_POOL_COUNT]` tracks file descriptors, backing filenames, allocated blocks, and in-memory records. Core pool functions are `kvp_file_init`, `kvp_update_mem_state`, `kvp_update_file`, `kvp_key_add_or_modify`, `kvp_get_value`, `kvp_key_delete`, and `kvp_pool_enumerate`. Host-facing network operations use `kvp_mac_to_ip`, `kvp_get_if_name`, `kvp_get_ip_info`, and `kvp_set_ip_info`. OS identity helpers include `kvp_get_os_info` and `kvp_get_domain_name`.

## Control Flow and State

Startup parses `--no-daemon`, `--debug`, and `--help`, optionally daemonizes, initializes syslog, reads OS/domain data, and creates or loads `/var/lib/hyperv/.kvp_pool_<n>` files. The daemon opens `/dev/vmbus/hv_kvp`, writes a `KVP_OP_REGISTER1` message, then blocks in `poll`. Each request is read, decoded by operation, answered in the same message buffer, and written back to the kernel. Short reads or writes reopen the device, which handles hibernation and kernel-side reset cases. Persistent state lives in fixed-size record files under `/var/lib/hyperv`; `fcntl` write locks protect file reads and rewrites. Network SET operations also persist generated `ifcfg-<ifname>` and `<ifname>.nmconnection` files under `/var/lib/hyperv` before invoking `hv_set_ifconfig`.

## Dependencies and Integration Points

The daemon depends on the Hyper-V kernel vmbus KVP device, `/sys/class/net`, `/etc/os-release` or legacy release files, libc networking APIs, `ip`, and helper scripts under `KVP_SCRIPTS_PATH` such as `hv_get_dns_info`, `hv_get_dhcp_info`, and `hv_set_ifconfig`. It integrates with host Hyper-V Data Exchange and network injection flows. The generated NetworkManager and ifcfg files are intended as an intermediate distro-neutral contract between the C daemon and the external distro-specific script.

## Risks

The daemon runs as a privileged service and executes shell commands assembled from configured script paths and interface names, so argument construction and deployment paths are security-sensitive. Pool file rewrites rewrite the whole record array and exit on many I/O failures, which can terminate the service if `/var/lib/hyperv` is unavailable. Network parsing has many fixed-size buffers and semicolon-delimited formats; malformed or oversized host-provided address, gateway, DNS, or subnet strings can lead to failed configuration. IPv6 and NetworkManager method decisions are subtle, especially when DHCP is true but only IPv6 data is supplied. External helper failures are reported as Hyper-V failures but may leave intermediate config files behind.

## Test Signals

Useful tests include building the tool against the current kernel UAPI, running KVP set/get/delete/enumerate operations through `/dev/vmbus/hv_kvp`, checking file locking and reload behavior with concurrent pool modifications, validating auto enumeration values, and testing GET/SET IP flows on IPv4, IPv6, DHCP, static, no-address, and multi-address interfaces. Integration tests should confirm helper script invocation, generated `ifcfg` and `.nmconnection` contents, device reopen after simulated hibernation, and error propagation to the host.

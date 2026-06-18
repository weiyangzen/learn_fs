# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/vxlan.c

## Purpose
`vxlan.c` manages the hardware VXLAN UDP destination-port table for mlx5 Ethernet offloads. It creates a per-device VXLAN object, programs firmware add/delete commands for UDP ports, tracks configured ports in an RCU hash table, and resets to the default IANA port.

## Important APIs, types, and functions
Public APIs are `mlx5_vxlan_create()`, `mlx5_vxlan_destroy()`, `mlx5_vxlan_add_port()`, `mlx5_vxlan_del_port()`, `mlx5_vxlan_lookup_port()`, and `mlx5_vxlan_reset_to_default()`. `struct mlx5_vxlan` stores the core device, hash table, and mutex. `struct mlx5_vxlan_port` stores hash linkage and UDP port. Firmware helpers issue `ADD_VXLAN_UDP_DPORT` and `DELETE_VXLAN_UDP_DPORT`.

## Control flow
Creation returns `-EOPNOTSUPP` encoded in the pointer when VXLAN stateless offload is unsupported or the function is not a PF. Otherwise it allocates the object, initializes the mutex/hash, and adds the default IANA VXLAN port. Add allocates a software node, sends the firmware add command first, then inserts into the RCU hash under the mutex. Delete locks, finds the port, removes it from the RCU hash, waits for readers with `synchronize_rcu()`, sends the firmware delete command, frees the node, and returns `-ENOENT` if the port is unexpectedly absent. Reset iterates configured ports and removes every port except the IANA default.

## State and persistence behavior
State is volatile software hash entries plus hardware UDP destination-port table entries. Destroy deletes the default port, warns if the hash is not empty, and frees the object. Unsupported state is represented by an error pointer, and all public helpers tolerate that through `mlx5_vxlan_allowed()`.

## Dependencies and integration points
The file depends on Linux VXLAN constants, RCU hash APIs, mutexes, mlx5 command execution, and PF/offload capability checks. It is created/destroyed by the core lifecycle in `main.c` and used by tunnel offload code that needs hardware recognition of VXLAN ports.

## Risks and edge cases
`mlx5_vxlan_add_port()` does not check for an existing port before programming hardware, so callers should avoid duplicates. Delete ignores the return from the firmware delete command and always returns the software lookup status. Creation does not roll back object allocation if adding the default port fails. RCU lookup returns false for unsupported/error-pointer objects.

## Test signals
Test supported PF creation, unsupported VF/capability error pointers, default port programming, add/delete/lookup for custom ports, reset-to-default, duplicate add behavior, firmware command failure injection, destroy with no extra ports, and concurrent RCU lookup during deletion.

# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/devlink_in_netns.sh

Purpose: Verifies that a netdevsim devlink instance created inside a network namespace is visible and has usable port-to-netdev mappings from that namespace.

Important APIs/functions: `port_netdev_get` parses `devlink -N testns1 port show -j` with `cmd_jq`. `check_devlink_test` runs `devlink -N testns1 dev show`. `check_ports_test` validates each port netdev exists with `ip -n testns1 link show`.

Control flow: `setup_prepare` loads netdevsim, creates `testns1`, and writes `BUS_ADDR PORT_COUNT` to `/sys/bus/netdevsim/new_device` from inside the namespace. After sysfs net directory appears, `tests_run` executes the two checks. Cleanup deletes the netdevsim device, namespace, and module.

State and persistence: Creates one namespace and one netdevsim device with four ports. State is expected to disappear after writing `BUS_ADDR` to `del_device` and deleting the namespace.

Dependencies and integration: Uses forwarding `lib.sh`, `devlink`, `ip netns`, `jq`, `/sys/bus/netdevsim`, and root privileges.

Risks: The script busy-waits without sleep for sysfs visibility. Device deletion is written from the initial namespace and assumes the bus device remains reachable. Failures in namespace creation or device creation before trap setup could leave state.

Test signals: Devlink device show succeeds in the namespace, every devlink port reports a netdev name, and each reported netdev is found by namespaced `ip link`.

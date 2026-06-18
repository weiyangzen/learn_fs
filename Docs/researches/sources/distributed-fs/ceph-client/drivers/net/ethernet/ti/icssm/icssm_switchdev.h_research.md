# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switchdev.h

## Purpose
This small header declares the ICSSM switchdev notifier interface and port-device predicate shared between the main driver and switchdev implementation.

## Important APIs, types, and functions
- `icssm_prueth_sw_register_notifiers(struct prueth *prueth)` registers switchdev notifier blocks.
- `icssm_prueth_sw_unregister_notifiers(struct prueth *prueth)` unregisters them.
- `icssm_prueth_sw_port_dev_check(const struct net_device *ndev)` identifies ICSSM ports eligible for switchdev handling.

## Control flow
`icssm_prueth.c` calls register during probe after netdev registration and unregister during remove. Switchdev helper calls use the predicate to filter events to ICSSM devices with L2 firmware offload capability.

## State and persistence behavior
The header itself stores no state. The declared functions mutate notifier blocks in `struct prueth` and inspect netdev features/ops.

## Dependencies and integration points
It includes `icssm_prueth.h`, so users gain the ICSSM core type definitions. It is included by `icssm_prueth_switch.h` and implemented by `icssm_switchdev.c`.

## Risks and edge cases
- The predicate is central to avoiding unrelated switchdev events; an overly broad match could mis-handle another netdev, while an overly narrow match disables offload.
- Include coupling with the full ICSSM header increases rebuild scope.

## Test signals
Probe/remove should register and unregister without leaks. Bridge and switchdev operations on non-ICSSM devices should be ignored, while ICSSM offload-capable ports should accept relevant events.

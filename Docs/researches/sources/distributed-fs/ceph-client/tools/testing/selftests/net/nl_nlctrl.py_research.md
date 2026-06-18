<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_nlctrl.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_nlctrl.py

## Purpose
This Python kselftest validates the `nlctrl` generic-netlink controller family, especially family discovery and policy dump reporting for split-op and full-op families.

## Important APIs, Types, And Functions
It uses `NlctrlFamily`, `NetdevFamily`, `EthtoolFamily`, `ksft_run()`, `ksft_exit()`, and assertion helpers. Test functions are `getfamily_do()`, `getfamily_dump()`, `getpolicy_dump()`, and `getpolicy_by_op()`.

## Control Flow
The script queries the `netdev` family by name, rekeys its op list by command ID, and checks capability flags and notification-only exclusions. It dumps all families and confirms `nlctrl` and `netdev` are present. It then uses family helpers to retrieve operation policies for netdev split ops and ethtool full ops, checking that do/dump policies exist or are absent as expected and that attribute names are resolved.

## State, Persistence, And Dependencies
There is no persistent state; all work is generic-netlink querying. It depends on the Python netlink helper library, `netdev` and `ethtool` generic-netlink families, and kernel support for controller policy dumps.

## Integration Points
This file verifies the metadata layer consumed by other YNL-based tests. It ensures generic-netlink family operation flags and policy resolution are visible and correctly decoded for netdev and ethtool.

## Risks
It hard-codes command IDs such as netdev `dev-get` 1, `qstats-get` 12, and `napi-set` 14, so legitimate UAPI renumbering would require updates. Family availability is kernel-configuration dependent.

## Test Signals
Kselftest assertions check family names/IDs, op capability flags, dump contents, policy dictionaries, absence of notification-only ops, and no unresolved `attr-N` names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_nlctrl.py -->

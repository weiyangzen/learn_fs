# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vlan_bridge_binding.sh

Purpose: Tests VLAN upper-device `bridge_binding` operstate behavior on a VLAN-filtering bridge with multiple ports and VLAN memberships.

Important APIs/functions: uses `lib.sh` ADF/defer helpers (`adf_ip_link_add`, `adf_bridge_vlan_add`, `defer_scope_push/pop`, `tests_run`) plus `jq`. `setup_prepare()` creates bridge `br`, veth ports `d1..d3`, enslaves ports, and configures VLAN IDs 11-14 with different membership sets. `add_vlans()` creates `br.<vid>` VLAN upper devices with `bridge_binding` on/off. `check_operstate()` busywaits and maps JSON `operstate` to boolean.

Control flow: declared `ALL_TESTS` covers binding on, binding off, toggles on/off, and toggles while lower or upper devices are down. `do_test_binding()` repeatedly downs combinations of d1/d2/d3, optionally injects a bridge_binding toggle, checks expected operstates for VLAN uppers, then restores via defer scopes.

State and persistence: bridge, veths, VLAN devices, bridge VLAN database, and interface states are temporary in current namespace/test context. Defer scopes restore state within tests; exit trap cleans remaining scopes. No files.

Dependencies and integration: requires root, bridge VLAN filtering, VLAN devices, `jq`, iproute2, and `lib.sh` defer/ADF helpers.

Risks: operstate transitions are asynchronous, so checks depend on `busywait 1000`. Expected state vectors are tightly coupled to configured VLAN memberships.

Test signals: `log_test` reports each high-level scenario. Failures show actual/expected operstate from `check_err`.

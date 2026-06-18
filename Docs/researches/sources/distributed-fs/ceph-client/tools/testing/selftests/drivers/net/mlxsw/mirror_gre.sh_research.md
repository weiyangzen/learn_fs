# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mirror_gre.sh

## Purpose

Functional GRE mirror offload tests for keyful and software GRE modes, TOS, TTL, and failure handling.

## Important APIs, Types, and Functions

Sources `mirror_lib.sh`, `mirror_gre_lib.sh`, and `mirror_gre_topo_lib.sh`. It defines setup/cleanup for keyful and software variants, `test_span_gre_ttl_inherit`, `test_span_gre_tos_fixed`, `test_span_failable`, and wrapper tests `test_keyful`, `test_soft`, `test_tos_fixed`, and `test_ttl_inherit`.

## Control Flow

Setup prepares a six-netif mirror topology with hosts, bridge/switch ports, and GRE tunnel endpoints. Each test configures a mirror action from ingress traffic into a GRE/gretap tunnel, injects traffic, and checks captured mirrored packets for expected key, TOS, TTL, or failure behavior. Cleanup removes mirror filters, tunnels, and topology state.

## State and Persistence Behavior

State includes GRE tunnel devices, bridge membership, TC mirror actions, routes/addresses, and capture filters created by shared mirror helpers.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It relies heavily on the forwarding mirror helper libraries for topology and packet validation.

## Risks and Edge Cases

Risk is concentrated in tunnel option support and capture interpretation. GRE key support, inherited TTL/TOS handling, and offload failure paths vary by kernel and device revision. Shared helper cleanup must remove all TC mirror rules.

## Test Signals

Signals are mirror helper pass/fail results, packet capture checks on GRE tunnel endpoints, and `log_test` wrappers.

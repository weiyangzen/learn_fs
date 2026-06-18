# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ioam6.sh

Purpose: End-to-end IPv6 IOAM selftest covering local IOAM configuration validation, encapsulating-node output behavior, and transit-node input behavior for preallocated trace options in inline and encap modes.

Important APIs and commands: Sources `lib.sh`; uses `setup_ns`, `cleanup_ns`, `ip ioam namespace`, `ip ioam schema`, `ip -6 route encap ioam6`, IOAM sysctls under `net.ipv6`, `ping6`, `modprobe ip6_tunnel`, and `ioam6_parser`. The `ALPHA` and `BETA` arrays are the authoritative data model shared with the parser.

Control flow: `check_kernel_compatibility` verifies route-level IOAM support and optional tunnel support. `setup` builds Alpha, Beta, and Gamma namespaces with two veth links, routing, IOAM namespaces, schemas, node IDs, interface IDs, and forwarding. `run` executes LOCAL tests with no mode, inline mode, and encap mode; then OUTPUT tests with Beta IOAM disabled; then INPUT tests after removing Alpha namespace state so Beta is the node under inspection. Each packet test changes the Alpha route, starts `ioam6_parser` in Gamma, sends one ping, and records pass/fail/skip.

State and persistence: All state is temporary netns routing, sysctls, IOAM namespace/schema tables, and optional `ip6_tunnel` module load state. Cleanup removes namespaces and unloads the module only if the test loaded it.

Dependencies and integration: Depends on root, recent kernel `CONFIG_IPV6_IOAM6_LWTUNNEL`, iproute2 IOAM support, optional `ip6_tunnel`, and the parser binary.

Risks: Shell arrays must stay synchronized with `ioam6_parser.c`. The test matrix is large and route mutations must be reset after each case. Encap cases are skipped if tunnel support cannot be loaded.

Test signals: Nonzero `nfailed` fails the test. Passing signals include accepted/rejected route encap syntax, correct trace sizes and bit support, proper overflow handling, and parser-verified packet bytes.

# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/net_test.c

## Purpose

`net_test.c` is the Landlock network selftest matrix for TCP bind/connect rules, protocol filtering, port semantics, layered rulesets, combined filesystem/network rules, and audit output. It verifies that only TCP over IPv4/IPv6 is governed by `LANDLOCK_ACCESS_NET_BIND_TCP` and `LANDLOCK_ACCESS_NET_CONNECT_TCP`, while UDP, MPTCP variants, AF_UNIX sockets, and invalid address-family combinations keep kernel-native behavior.

## Important APIs, Types, and Functions

The file uses kselftest fixtures, `struct service_fixture` and `struct protocol_variant` from `common.h`, Landlock syscalls through `landlock_create_ruleset()`, `landlock_add_rule()`, and `enforce_ruleset()`, and socket APIs including `socket()`, `bind()`, `listen()`, `connect()`, `accept()`, `getsockname()`, and AF_UNSPEC disconnects. Helpers such as `set_service()`, `socket_variant()`, `get_addrlen()`, `bind_variant_addrlen()`, `connect_variant_addrlen()`, and `test_bind_and_connect()` normalize protocol-specific setup.

## Control Flow and State

Fixture variants cover no-sandbox and TCP-sandbox modes across IPv4, IPv6, TCP, MPTCP, UDP, and UNIX sockets. Each test creates a private network namespace, raises loopback, builds one or more ruleset layers, forks clients when needed, and compares expected success, `EACCES`, `EINVAL`, `EAFNOSUPPORT`, `ECONNREFUSED`, or `EISCONN`. State is mainly per-process Landlock domain state, per-socket bound/connected state, selected port numbers, audit records, and temporary capabilities used for namespace setup or low-port binding.

## Dependencies and Integration Points

It depends on Landlock ABI network rights, Linux socket semantics, kselftest harness macros, audit helpers, loopback setup via `ip link`, and capability helpers. It integrates with `common.h`, `audit.h`, and the Landlock selftest Makefile.

## Risks and Test Signals

Regression risks include host-vs-network byte-order confusion, incorrect AF_UNSPEC handling, accidental restriction of UDP/MPTCP/UNIX paths, layer union/intersection mistakes, mishandling of port 0 or `UINT16_MAX`, and audit format drift. Strong signals are exact errno assertions, successful client/server byte transfer, audit records matching `net.bind_tcp` or `net.connect_tcp`, and absence of unexpected access records.

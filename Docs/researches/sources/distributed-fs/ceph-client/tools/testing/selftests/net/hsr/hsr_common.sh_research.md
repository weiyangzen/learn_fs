# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/hsr_common.sh

## Purpose

This shell library provides shared helpers for HSR and PRP kselftests: IP version detection, short ping checks, longer duplicate/loss-sensitive ping checks, failure stopping, and prerequisite validation.

## Important APIs, Types, and Functions

It sources `../lib.sh`, initializes `ret` and `ksft_skip`, and defines `is_v6`, `do_ping`, `do_ping_long`, `stop_if_error`, and `check_prerequisites`. It expects caller-defined namespace variables and an `ipv6` boolean.

## Control Flow

Callers source this file, then use `check_prerequisites`, create namespaces/topologies, and call `do_ping` or `do_ping_long`. IPv6 pings are skipped when `ipv6=false`; failures set global `ret=1`, and `stop_if_error` exits if any previous check failed.

## State and Persistence Behavior

It owns only shell variables and returns. It does not create network state directly, but its ping helpers observe connectivity and duplicate/loss behavior in caller-created namespaces.

## Dependencies and Integration Points

It depends on `../lib.sh`, `ip`, `ping`, namespace names from `setup_ns`, and the kselftest return code convention. It is the shared integration layer for `hsr_ping.sh`, `hsr_redbox.sh`, and `prp_ping.sh`.

## Risks and Edge Cases

`do_ping_long` parses localized ping output after forcing `LANG=C`, but format changes can still break duplicate/loss detection. The sed expression expects two-digit transmitted/received fields for 10-packet runs. IPv6 checks silently return success when IPv6 is disabled, which is intentional for `-4` modes.

## Test Signals

Signals are process return codes from ping, exact long-ping parsing for `10 transmitted 10 received 0% loss`, and `ret` remaining zero across caller test phases.

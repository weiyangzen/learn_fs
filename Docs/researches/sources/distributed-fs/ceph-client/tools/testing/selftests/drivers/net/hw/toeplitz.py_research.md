
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/toeplitz.py`

## Purpose
Python harness for the Toeplitz RX hash verifier. It configures RSS hash function state, optionally configures RPS, sends TCP/UDP IPv4/IPv6 traffic, and runs the compiled `toeplitz` receiver.

## Important APIs, Types, And Functions
- `_check_rps_and_rfs_not_configured()` prevents external RPS/RFS state from contaminating CPU selection tests.
- `_get_irq_cpus()` maps RX queues to IRQ CPUs through `NetdevFamily.queue_get()` and `napi_get()`.
- `_configure_rps()` writes per-queue `rps_cpus` sysfs masks.
- `_test_variants()` creates rxhash-only, RSS CPU, and RPS CPU variants for TCP/UDP and IPv4/IPv6.
- `test()` builds the receiver command and sends repeated traffic until the receiver exits.

## Control Flow
Each variant requires the IP version, checks `receive-hashing: on`, forces ethtool netlink RSS hash function to Toeplitz with no input transform if necessary, chooses a destination port, builds `toeplitz` command arguments, configures RSS CPU map or RPS mask for grouped tests, starts the receiver with ksft readiness, and repeatedly sends packets from the remote until the receiver finishes.

## State And Persistence
Mutates RSS `hfunc` and `input-xfrm` only if needed and restores via `defer()`. RPS mode writes sysfs `rps_cpus` masks for all RX queues and defers clearing them.

## Dependencies And Integration Points
Depends on `toeplitz` binary in the same directory, `NetDrvEpEnv`, ethtool netlink, `NetdevFamily`, `socat` on remote, IRQ affinity files, and sysfs RPS knobs.

## Risks
RSS CPU tests require IRQs mapped to single CPUs; RPS tests require spare CPUs below the C helper's `RPS_MAX_CPUS`. Existing RPS/RFS configuration causes skips because it would change CPU selection.

## Test Signals
The harness reports receiver stdout/stderr through ksft logs. Success requires the C receiver to see enough packets and exit with no hash/RSS/RPS verification errors.

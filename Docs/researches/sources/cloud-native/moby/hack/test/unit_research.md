# sources/cloud-native/moby/hack/test/unit

## Purpose
Runs Go unit tests across Moby modules and writes coverage/JUnit/report artifacts.

## Important APIs and Types
Uses `TESTFLAGS`, `TESTDIRS`, build tags `netgo journald`, `gotestsum`, module package lists, and bundle outputs under `bundles/`.

## Control Flow, State, and Persistence
The script detects whether requested packages fall under `api`, `client`, root, or `libnetwork`, runs separate module tests with `-mod=readonly`, excludes vendor/integration packages for root tests, builds/installs `docker-proxy` if bridge tests need it, runs libnetwork tests serially, and optionally reruns `TestFlaky.*` with retries. It writes JSON, JUnit, and coverage files under `bundles`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Go, `gotestsum`, module layout, and optionally docker-proxy. Risks include shell word splitting in test flags/package lists, module selection misses, and flaky reruns hiding nondeterminism. The produced reports and exit status are the direct test signals.

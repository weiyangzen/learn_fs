# sources/cloud-native/cri-o/test/cni_plugin_helper.bash

## Purpose
CNI bridge wrapper used by integration tests to validate CRI-O CNI argument passing, health/status behavior, and malformed-result handling.

## Important APIs, Types, And Functions
Handles CNI `VERSION` and `STATUS`, parses `CNI_ARGS`, writes observed arguments to `$TEST_DIR/plugin_test_args.out`, sources `$TEST_DIR/cni_plugin_helper_input.env`, invokes `/opt/cni/bin/bridge`, and optionally emits malformed JSON when `DEBUG_ARGS=malformed-result`.

## Control Flow
For `VERSION`, prints supported CNI versions and exits. For `STATUS`, returns failure when a sentinel file exists. For normal commands, it validates required CNI/Kubernetes variables, records them, consumes a one-shot env file, runs the real bridge plugin, propagates failures, and either forwards or corrupts the result.

## State And Persistence
Writes `plugin_test_args.out` and removes `cni_plugin_helper_input.env`. Reads a test-specific status sentinel and env file.

## Dependencies And Integration Points
Installed into isolated CNI bin directories by `helpers.bash` with `%TEST_DIR%` replaced. Depends on the real bridge plugin at `/opt/cni/bin/bridge`.

## Risks And Test Signals
The wrapper is path-sensitive and assumes bridge lives at `/opt/cni/bin/bridge`, even though tests copy CNI binaries elsewhere. It includes an unusual non-printing character after the STATUS block in the current source, which could affect shell parsing on strict tooling.

# sources/cloud-native/ostree/tests/test-sysroot-c.c

## Purpose
This C integration test validates `ostree_sysroot_load_if_changed()` around real sysroot deployment changes.

## Important APIs, Types, And Functions
It uses `ot_test_setup_sysroot`, `ostree_sysroot_load`, `ostree_sysroot_load_if_changed`, `g_spawn_command_line_sync`, `g_spawn_check_exit_status`, and CLI commands `ostree pull-local` and `ostree admin deploy`.

## Control Flow
`run_sync()` executes shell commands and validates exit status. `test_sysroot_reload()` loads the sysroot, confirms `load_if_changed` initially reports unchanged, pulls a test ref into the sysroot repo, deploys it with kernel args and OS name, then confirms `load_if_changed` reports changed once and unchanged on the next call.

## State And Persistence
State includes the test sysroot, sysroot repository, pulled local ref, deployment directories, bootloader/deployment metadata, and in-memory sysroot loaded state.

## Dependencies And Integration Points
This integrates libostree sysroot APIs with command-line admin deployment, local pull, boot deployment metadata, and the test sysroot fixture.

## Risks
Change detection must update after deployment writes and then become stable. CLI command failure is surfaced through GLib errors. The test assumes the fixture creates `sysroot` and `testos-repo` in the working directory.

## Test Signals
The GLib path `/sysroot-reload` fails on command execution errors or incorrect `changed` booleans.

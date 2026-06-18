# sources/cloud-native/containers-storage/tests/test_drivers.bash

Purpose: driver matrix launcher for the `containers-storage` Bats tests. It discovers supported graph drivers and invokes `test_runner.bash` once per selected driver.

Important APIs and control flow: helper functions `aufs`, `btrfs`, `overlay`, and `zfs` test availability through `modprobe`, `/proc/filesystems`, or filesystem type checks on `TMPDIR`. If `STORAGE_DRIVER` is unset, it builds a default list starting with `vfs` and conditionally appends available drivers; otherwise it uses the provided driver only. The final loop prints a Bats-style header and runs `test_runner.bash` with `STORAGE_DRIVER` exported.

State and persistence: no persistent state. It reads `TMPDIR` and `STORAGE_DRIVER`, and relies on `test_runner.bash` plus helpers to create per-test storage roots.

Dependencies and integration: Linux-focused due to `/proc/filesystems`, `modprobe`, and `stat -f -c`. Integrates with Bats through the downstream runner and with kernel storage modules for driver availability.

Risks: shell tests are unquoted around `TMPDIR`, and driver probing assumes GNU `stat`. `set -e` starts only after discovery, so probe failures before the loop are tolerated. Non-Linux platforms or minimal containers may under-detect drivers.

Test signals: its success is measured by all delegated Bats tests passing for each detected driver; discovery output also makes the active driver visible in TAP logs.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_unix_test.go -->
# sources/cloud-native/moby/daemon/command/daemon_unix_test.go

## Purpose
Validates Unix-only daemon configuration loading for daemon flags, networking JSON keys, map options, and boolean defaults that are true in the default config.

## Important APIs, Types, And Functions
Uses `defaultOptions`, `loadDaemonCliConfig`, `config.Reload`, and platform-installed flags such as `selinux-enabled`.

## Control Flow
Tests prepare temp daemon JSON files, install default flags, optionally set flags, load the merged config, and assert platform-specific fields. Reload is invoked to ensure normalized boolean values do not cause later conflicts.

## State And Persistence Behavior
Only temp config files and in-memory flag sets are used. The reload callback observes the parsed config but does not alter daemon state.

## Dependencies And Integration Points
Connects command parsing to `daemon/config` Unix platform fields such as SELinux, bridge IP fields, userland-proxy defaults, and log options.

## Risks And Test Signals
Signals include `userland-proxy=false` surviving merge/reload, `bip`, `bip6`, and `ip` decoding into correct fields, and default `EnableUserlandProxy` remaining true when absent.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_unix_test.go -->

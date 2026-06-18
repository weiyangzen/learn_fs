# sources/cloud-native/moby/integration/plugin/logging/logging_linux_test.go

## Purpose
Linux logging plugin regression test ensuring a container continues producing output and the daemon does not log broken-pipe errors when a log plugin closes its file immediately.

## Important APIs, Types, And Functions
Uses `daemon.New`, daemon flags disabling iptables/ip6tables plus `--init`, logging `createPlugin` with `close_on_start`, `PluginEnable`, `container.Run` with `WithLogDriver("test")`, `ContainerAttach`, and direct daemon log file scanning.

## Control Flow
The test starts a daemon, creates/enables the close-on-start log plugin, runs a container that emits `hello` repeatedly, attaches to stdout, reads five lines asynchronously with a timeout, then scans the daemon log file and asserts no line contains `broken pipe`.

## State And Persistence Behavior
Temporary plugin and container state are created and removed. The daemon log file is read as observational state.

## Dependencies And Integration Points
Depends on local daemon, plugin fixture binary, container attach stream, daemon logging, and Linux-only plugin support.

## Risks
The daemon log scan is acknowledged as hacky and could miss differently worded failures or fail on unrelated log text. Timing depends on container output and attach stream readiness.

## Test Signals
Signals are successful plugin enable, receipt of five stdout lines within 60 seconds, and absence of `broken pipe` in daemon logs.

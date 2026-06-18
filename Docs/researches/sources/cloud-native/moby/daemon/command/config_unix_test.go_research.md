# Research: sources/cloud-native/moby/daemon/command/config_unix_test.go

## sources/cloud-native/moby/daemon/command/config_unix_test.go

Purpose: Unix-only test for parsing the `--default-shm-size` daemon flag.

`TestDaemonParseShmSize` creates a pflag set and default config, installs Unix config flags, asserts the default shared memory size is 64 MiB, sets `default-shm-size` to `128M`, and asserts the config value updates to 128 MiB.

State is local config mutation. Dependencies are daemon config, pflag, and gotest assertions. The test protects a visible CLI compatibility default and parser behavior. Gaps include invalid size inputs and other Unix flags.

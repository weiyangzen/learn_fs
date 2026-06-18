# sources/control-plane/rook/cmd/rook/ceph/config.go

## Purpose

Implements `rook ceph config-init`, a helper that writes a minimal Ceph config for non-Ceph daemons such as nfs-ganesha.

## Important APIs, Types, and Functions

`configCmd` requires `--keyring` and `--username`. `initConfig()` validates flags, reads `ROOK_CEPH_MON_HOST`, builds a minimal `[global]` plus user section config, writes it to `cephclient.DefaultConfigFilePath()` with mode `0444`, and logs the file.

## Control Flow

`init()` registers required flags and assigns `RunE`. Execution sets log level, logs startup flags, validates values, reads the monitor host env var, writes the config file, and returns.

## State and Persistence Behavior

The command writes `/etc/ceph/ceph.conf` or the default path returned by the Ceph client package. The config contains monitor hosts and keyring path for the supplied user.

## Dependencies and Integration Points

It integrates with Cobra, Rook logging, Ceph client default config path, utility file logging, and pod environment variables shared by Ceph daemon pods.

## Risks and Edge Cases

The config is built by string concatenation from CLI/env values; these are expected controlled pod inputs. Missing keyring, username, or monitor host terminates fatally. The written file is world-readable, but it contains a keyring path rather than the key itself.

## Test Signals

Tests should verify required flag handling, missing env failure, file content, permissions, and default path behavior. Integration signals come from daemons that rely on generated config.

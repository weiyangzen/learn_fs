# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/idgen.go

This file contains a single helper, `newID`, which returns `xid.New().String()`. It is used by `NewDaemon` to assign each daemon a unique stable identifier before daemon options derive socket, config, and log paths from the ID.

The dependency is `github.com/rs/xid`, which produces compact globally unique identifiers without needing an external sequence store. There is no local persistence in this file, but the generated ID becomes part of persisted `daemon.ConfigState`, per-daemon config directories, API socket directories, log paths, supervisor names, manager cache keys, and daemon-image metrics labels.

The main risk is not algorithmic uniqueness but lifecycle coupling: options such as `WithSocketDir` and `WithConfigDir` assume the ID already exists, and manager recovery overwrites `Daemon.States` from stored state after constructing a placeholder daemon. There are no direct tests for ID generation. Indirect coverage comes from daemon creation paths and manager cache tests that use explicit IDs.

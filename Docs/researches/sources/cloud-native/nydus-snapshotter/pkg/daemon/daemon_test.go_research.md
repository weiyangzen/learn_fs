# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/daemon_test.go

This test file targets `Daemon.UpdateAuthConfig`. `TestMain` initializes global snapshotter configuration so daemon config serialization can run safely. `minimalFuseConfig` creates a small valid `daemonconfig.FuseDaemonConfig` using a registry backend.

`TestUpdateAuthConfig` covers three cases: shared daemon basic auth updates a per-snapshot config and calls `PUT /api/v1/config?id=/snap-1`; dedicated daemon basic auth updates root config and calls `id=/`; bearer-token style credentials update disk only and skip the API because runtime token reload is not supported. The test pre-creates config files, starts a Unix-socket mock API server, injects a `NydusdClient` into the daemon to avoid socket wait, then validates both API body and on-disk config content.

The test is valuable because auth update spans file persistence and live daemon state. It confirms API ID selection based on daemon mode and validates basic-auth base64 storage. It does not cover load failures, dump failures, API error propagation, fscache config shape, nil clients, or concurrent updates. Temporary directories and sockets are the only external state.

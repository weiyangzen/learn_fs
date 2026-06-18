## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/client.go

Purpose: centralizes containerd client creation and command context setup.

Important APIs/types/functions: `AppContext` and `NewClient`.

Control flow: `AppContext` applies namespace, optional timeout, and `SOURCE_DATE_EPOCH`. `NewClient` appends containerd timeout option, trims `unix://` socket prefix, creates a containerd client, and returns the prepared context plus cancel function.

State and persistence: no durable state; creates network/socket client connections and context metadata.

Dependencies and integration: global flags, config socket trimming, containerd client, namespaces, epoch, and logging.

Risks and test signals: callers must close the returned cancel function but this function does not close the containerd client. No direct tests here.

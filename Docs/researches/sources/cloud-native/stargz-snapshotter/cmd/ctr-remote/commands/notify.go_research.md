# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/notify.go

Purpose: Defines hidden `ctr-remote fanotify`, the helper process invoked by analyzer fanotify code.

Important API: `FanotifyCommand`. It is hidden from normal CLI help and expects one target path argument.

Control flow: The action reads the target argument, errors if absent, and calls `service.Serve(target, os.Stdin, os.Stdout)`. That service performs the fanotify protocol and event streaming.

State and persistence: No state in this command file; service-side fanotify state is managed in `analyzer/fanotify/service`.

Dependencies and integration: Integrated with `SpawnFanotifier`, which launches the ctr-remote binary with `fanotify /` in a separate mount namespace and communicates over stdio.

Risks: Requires stdin/stdout to be reserved for the protocol. Any logging to stdout from the helper would corrupt protocol messages; service warnings go to stderr.

Test signals: No direct tests. Integration requires privileged fanotify execution.

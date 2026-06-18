## sources/cloud-native/moby/daemon/logger/gcplogs/gcplogging.go

Purpose: Implements the `gcplogs` driver, sending container logs to Google Cloud Logging with optional GCE instance metadata and container metadata payloads.

Important APIs and types: `gcplogs` holds a `logging.Client`, `logging.Logger`, optional `instanceInfo`, and `containerInfo`. Payload type `dockerLogEntry` contains instance, container, and message. `initGCP` performs one-time metadata detection. Public functions are `New`, `ValidateLogOpts`, `Log`, `Close`, and `Name`.

Control flow and state: `initGCP` calls `metadata.OnGCE` once and, on GCE, populates package globals for project, zone, instance name, and ID. `New` selects project from metadata or `gcp-project`, requires a project, creates a Cloud Logging client, builds a GCE monitored resource when instance data is known or explicitly configured, pings the service, extracts extra attributes, builds container metadata, optionally includes command when `gcp-log-cmd=true`, and installs an `OnError` handler. Overflow errors increment a global atomic dropped-log counter and log first/every-1000th drop. `Log` sends an async logging entry with timestamp and structured payload, then returns the message to the pool. `Close` flushes and closes the client.

Dependencies and integration points: Uses `cloud.google.com/go/logging`, compute metadata service, Google monitored resource protobufs, logger extra attributes, containerd logging, and application default credentials.

Risks: `Log` returns nil after enqueueing to Cloud Logging; later delivery errors are asynchronous via `OnError`. Metadata globals are process-wide and only initialized once. Project discovery and client `Ping` can fail at driver construction. High log volume can drop entries through client overflow.

Test signals: No direct tests in this subset; registration file connects validator/driver to the factory.

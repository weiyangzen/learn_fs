<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/launch-simple-file -->
## sources/control-plane/longhorn-engine/package/launch-simple-file

Purpose: simple demo/dev launcher that starts an instance-manager daemon and creates an engine backed by one local file backend.

Important behavior: requires `volume`; defaults size to `1g` and frontend to `tgt-blockdev`; bind-mounts `/host/dev`; truncates `/volume/volume.img`; waits for instance-manager health at `localhost:8500`; then runs `longhorn-instance-manager engine create` with `--enable-backend file --replica file://$img`.

Control flow and state: creates or resizes `/volume/volume.img`, starts a background readiness-and-create function, then execs `longhorn-instance-manager daemon`.

Dependencies and integration points: uses `grpc_health_probe`, `truncate`, instance-manager engine create API, file backend support, and frontend support.

Risks: unquoted `[ -z $volume ]` style tests can misbehave for unusual values. Truncating the image path is destructive for existing data. Background engine creation races with daemon readiness by polling health only.

Test signals: manual/demo smoke test with a mounted `/volume` and health probe. Not a production orchestration path.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/launch-simple-file -->

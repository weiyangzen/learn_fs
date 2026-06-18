<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/engine-manager -->
## sources/control-plane/longhorn-engine/package/engine-manager

Purpose: shell wrapper used as a container command for engine-manager style startup.

Important behavior: bind-mounts `/host/dev` over `/dev`, starts `tgtd -f` in background with logs tee'd to `/var/log/tgtd.log`, then execs `longhorn-instance-manager "$@"`.

Control flow and state: mutates mount namespace and starts a background TGT daemon before replacing the shell with instance-manager. Writes TGT logs.

Dependencies and integration points: depends on privileged mount access, `/host/dev`, TGT, and `longhorn-instance-manager`. It is copied into the runtime image.

Risks: no `set -e`, so failed mount or failed TGT startup may not stop execution. Requires privileged container permissions. TGT log can grow unless externally managed.

Test signals: container startup and iSCSI frontend smoke tests should validate this script.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/engine-manager -->

# sources/control-plane/beegfs-csi-driver/pkg/beegfs/nodeserver.go

Purpose: Implements the CSI Node service for staging BeeGFS filesystems and bind-mounting volume directories into pod target paths. It also reports node identity and node service capabilities.

Important APIs/types/functions: `nodeCaps` advertises `STAGE_UNSTAGE_VOLUME`. `nodeServer` stores a BeeGFS ctl executor, node ID, plugin config, client config template path, and mounter. Constructors `newNodeServer` and `newNodeServerSanity` select real or fake dependencies. CSI methods include `NodeStageVolume`, `NodeUnstageVolume`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeGetInfo`, and `NodeGetCapabilities`; stats and node expansion are unimplemented.

Control flow: `NodeStageVolume` validates volume ID, staging path, and mount capability, builds a `beegfsVolume` from the staging path, requires the staging directory to exist, writes client config files, confirms the BeeGFS target directory with `beegfs-ctl stat`, mounts BeeGFS if needed, then best-effort writes an empty node tracking file under `.csi/.../nodes/<nodeID>`. `NodePublishVolume` validates inputs, reconstructs the staged volume, checks the target directory exists in BeeGFS via ctl stat, creates target path if missing, skips if already bind mounted, adds `bind` and optional `ro` to mount flags, sanitizes options, and bind-mounts the volume subdirectory to the target path. `NodeUnstageVolume` best-effort removes the node tracking file before unmounting and cleaning generated client files while leaving the staging directory for the CO. `NodeUnpublishVolume` cleans up the bind mount target.

State and persistence: Writes client config files into the staging path, mounts BeeGFS at staging path, bind-mounts volume directories at publish target paths, and creates/removes node tracking files in the mounted BeeGFS `.csi` tree. Node tracking is best effort: failures are logged but do not fail stage/unstage.

Dependencies and integration points: Uses CSI protobufs, gRPC status codes, BeeGFS ctl executor abstraction, `writeClientFiles`, `mountIfNecessary`, `unmountAndCleanUpIfNecessary`, and Kubernetes mount-utils. It coordinates with controller deletion waiting through `.csi/.../nodes` files.

Risks: Read-only bind mount behavior is documented as limited when running inside containers because read-only may not propagate outside the plugin container for all COs. Node tracking best-effort failures reduce delete safety. No in-flight lock is used on the node side, so concurrent publish/stage operations rely on mount idempotency and external CO behavior. `NodePublishVolume` uses fstype `beegfs` for a bind mount, which follows existing mount-utils behavior but may be platform-sensitive.

Test signals: CSI sanity tests exercise node methods through the full in-process driver. There are no dedicated node unit tests in this subset, so detailed edge cases rely on sanity coverage and helper tests.

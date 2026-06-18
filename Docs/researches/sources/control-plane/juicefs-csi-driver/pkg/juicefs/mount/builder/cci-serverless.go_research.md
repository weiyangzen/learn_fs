# sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/cci-serverless.go

Purpose: builds CCI serverless mount sidecar pod specs for JuiceFS, adapting common mount-pod generation to a non-privileged serverless environment.

Important APIs and types: constants define CCI annotation/driver values. `CCIBuilder` embeds `ServerlessBuilder`, PVC, and app pod context. `NewCCIBuilder` constructs it from a `JfsSetting`, capacity, app pod, and PVC. `NewMountSidecar` creates the sidecar pod, adds post-start mount/quota checking, serverless env vars, CCI-specific volumes, cache volumes, and the shell command. `OverwriteVolumes` rewrites app volumes to a CCI CSI `gpath` volume using the mountpoint. `OverwriteVolumeMounts` forces mount propagation to `None`. `genCCIServerlessVolumes` and `genNonPrivilegedContainer` build the check-mount secret volume and container security context.

Control flow: `NewMountSidecar` starts from `genCommonJuicePod`, computes capacity/community/quota path, ensures a lifecycle exists, appends env and volume configuration, then sets command to init plus mount commands. The post-start hook invokes the check-mount script with escaped subpath/name/quota/mount values and logs to the container stdout.

State and persistence behavior: no state is persisted by the builder itself. The produced pod spec will later create Kubernetes pod, secret volume, cache volumes, lifecycle hooks, and CCI CSI volume mounts.

Dependencies and integration points: integrates `BaseBuilder`, `ServerlessBuilder`, global config paths, common mount container names, CCI CSI driver annotations, Kubernetes core pod/volume APIs, and shell escaping.

Risks and test signals: correctness depends on the external check-mount script secret and CCI-specific CSI driver behavior. `SYS_ADMIN`/`MKNOD` are still requested despite "non-privileged" naming, so platform policy must allow those capabilities. No direct listed test covers this file.

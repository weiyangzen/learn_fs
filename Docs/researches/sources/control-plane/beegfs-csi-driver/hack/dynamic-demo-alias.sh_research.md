<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/dynamic-demo-alias.sh -->
# sources/control-plane/beegfs-csi-driver/hack/dynamic-demo-alias.sh

Purpose: sourced shell helper defining `csc` aliases for manual CSI RPC testing against a locally running BeeGFS CSI driver.

Important APIs and flow: initializes `SYS_MGMTD_HOST`, creates fake kubelet staging/publish directories under `/tmp`, and aliases controller/node calls such as `createvolume`, `nodestagevolume`, `nodepublishvolume`, `nodeunpublishvolume`, `nodeunstagevolume`, `deletevolume`, and capability validation. It exercises volume parameters for stripe patterns and permissions.

State and persistence: creates local `/tmp/kubelet` and `/tmp/csdatadir` paths and may create/delete BeeGFS directories through CSI calls.

Dependencies and integration points: requires `csc`, sudo access, a driver socket at `/tmp/csi.sock`, a running driver, and a BeeGFS management host.

Risks and test signals: aliases capture `SYS_MGMTD_HOST` at source time and use sudo/local mounts. Test by running the command sequence and inspecting CSI responses and mount paths.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/dynamic-demo-alias.sh -->

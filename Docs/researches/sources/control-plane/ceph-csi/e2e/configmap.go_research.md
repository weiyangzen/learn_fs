# sources/control-plane/ceph-csi/e2e/configmap.go

Purpose: creates, updates, and deletes the Ceph-CSI cluster configuration ConfigMap used by e2e-deployed drivers. It converts live Ceph monitor and cluster metadata into the `config.json` payload consumed by Ceph-CSI.

Important APIs/types/functions: `deleteConfigMap(pluginPath)` deletes the YAML-defined ConfigMap. `createConfigMap(pluginPath, c, f)` loads the template, discovers cluster ID and monitors, builds a `[]cephcsi.ClusterInfo`, fills RBD/CephFS/read-affinity fields, and creates or updates the ConfigMap. `createCustomConfigMap(c, pluginPath, clusterInfo)` writes multiple cluster entries with caller-specified `subvolumeGroup` and `radosNamespace`.

Control flow: default creation unmarshals `<pluginPath>/<configMap>`, calls `getClusterID()` and `getMons()`, marshals cluster info into `Data["config.json"]`, sets the target namespace, then updates an existing ConfigMap or creates one if not found. Upgrade testing forces the CephFS subvolume group to `csi` before writing the config. Custom creation builds one cluster info entry per map key, fills monitor lists, applies supported per-cluster options, marshals JSON, and updates the existing ConfigMap.

State and persistence: persists `config.json` in the `cephCSINamespace` ConfigMap. It embeds global `radosNamespace`, `subvolumegroup`, secret names, read-affinity labels, and current monitor endpoints. Tests often restart CSI pods after changing it so drivers reload state.

Dependencies and integration points: uses Kubernetes ConfigMap API, Ceph-CSI deploy API structs, `unmarshal()`, `getClusterID()`, `getMons()`, `retryKubectlFile()`, and global deployment constants. It is used by CephFS, NFS, RBD migration, and NVMe-oF deployment helpers.

Risks: Go map iteration in `createCustomConfigMap()` makes cluster order nondeterministic, which is usually fine but can complicate diffs. Unsupported keys in `clusterInfo` are silently ignored. Updating config without pod restart may not affect running CSI components. Upgrade-test mutation of global `subvolumegroup` can influence later tests if not reset.

Test signals: valid ConfigMap creation/update, JSON parsable by Ceph-CSI, monitor and cluster ID accuracy, expected subvolume group/rados namespace routing, and successful CSI pod operation after config changes.

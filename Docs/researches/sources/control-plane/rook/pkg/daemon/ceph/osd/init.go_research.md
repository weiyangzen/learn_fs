# sources/control-plane/rook/pkg/daemon/ceph/osd/init.go

This small file creates the bootstrap OSD keyring used by OSD provisioning.

It defines `bootstrapOsdKeyring` as `bootstrap-osd/ceph.keyring` and `createOSDBootstrapKeyring()`, which builds username `client.bootstrap-osd`, a keyring path under the provided root directory, monitor access `allow profile bootstrap-osd`, and a template renderer based on `bootstrapOSDKeyringTemplate` from `device.go`. It delegates actual key creation and persistence to `cephclient.CreateKeyring()`.

State is the keyring file written under the Ceph config/root directory and the Ceph auth key created or fetched by the shared keyring helper. Dependencies include `clusterd.Context`, `cephclient.ClusterInfo`, path joining, and the client keyring creation API.

Integration point is the OSD prepare/init path, where ceph-volume needs bootstrap credentials with limited monitor privileges. Risks are mostly inherited from `CreateKeyring()` and filesystem permissions; the local function has little branching. `device_test.go` verifies the file contains the bootstrap client stanza, key value, and monitor caps.

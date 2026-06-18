<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/connectionconfig.sh -->
# sources/control-plane/rook/pkg/operator/ceph/nvmeof/connectionconfig.sh

## Purpose
This embedded Bash script runs in the NVMe-oF gateway init container. It writes Ceph connection files, copies the admin keyring, renders `nvmeof.conf` from a ConfigMap template with pod runtime values, and asks Ceph to create/show the gateway.

## Important APIs and control flow
The script enables strict Bash flags, writes `/etc/ceph/ceph.conf` using `ROOK_CEPH_MON_HOST`, copies `/tmp/ceph/keyring` to `/etc/ceph/keyring`, sets file modes, replaces `@@POD_NAME@@`, `@@ANA_GROUP@@`, and `@@POD_IP@@` placeholders from `GATEWAY_NAME`, `ANA_GROUP`, and `POD_IP`, then runs `ceph "$@" nvme-gw create ... || true` and `ceph "$@" nvme-gw show ... || true`.

## State and persistence
It writes generated files into the pod's `/etc/ceph` volume. It also attempts to create/update Ceph NVMe gateway state through the Ceph CLI, but the command failures are ignored by `|| true`.

## Dependencies and integration points
The script is embedded by `spec.go` with `go:embed` and executed by `createCephConfigInitContainer`. It depends on mounted admin keyring, ConfigMap at `/config/nvmeof.conf`, pod IP env injection, Ceph CLI args passed from Rook helpers, and monitor host env vars.

## Risks and test signals
Ignoring `ceph nvme-gw create/show` failures can let the init container succeed even when Ceph-side gateway registration fails. Placeholder substitution is plain `sed`, so values containing sed metacharacters could be problematic. There are no direct shell tests in this subset; behavior is indirectly exercised through generated init-container specs and NVMe-oF controller tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/connectionconfig.sh -->

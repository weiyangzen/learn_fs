## sources/control-plane/longhorn-engine/scripts/integration-test

### Purpose
`scripts/integration-test` prepares and runs Longhorn engine integration tests inside an environment with instance managers, iSCSI tools, MinIO backup targets, backing files, and built engine binaries.

### Important APIs, Types, And Functions
The script creates a unique `TESTPREFIX`, defines `cleanupISCSI`, prepares backing/fixed directories, ensures `bin/longhorn` exists, bind-mounts `/host/dev` into `/dev` when available, exports S3 backup credentials and test certificates, creates raw/qcow2 backing files, copies engine binaries into instance-manager-accepted directories, starts two `longhorn-instance-manager` daemons, starts MinIO, sets `BACKUPTARGETS`, cleans Python caches, and runs `tox` in `integration` unless `NO_TEST` is set.

### Control Flow
`set -e` aborts on failures. Multiple `trap` registrations handle temporary directory cleanup and later instance-manager/iSCSI cleanup. The script starts background services, validates their PIDs with `ps`, then runs tests.

### State, Persistence, And Dependencies
It creates and removes `/tmp` replica directories, `/engine-binaries` content, `~/.minio/certs`, `/data/backupbucket`, and MinIO/instance-manager processes. Dependencies include `uuidgen`, `nsenter`, `iscsiadm`, `qemu-img`, `longhorn-instance-manager`, `minio`, `tox`, Python integration tests, and root-level mount permissions.

### Integration Points
This is the most complete local signal for engine behavior: rebuild, backup/restore, backing image, live upgrade, iSCSI, and instance-manager interactions.

### Risks
It assumes privileged container/host layout, can mount `/host/dev`, starts services on fixed ports, and writes fixed host paths. Cleanup depends on traps and can leave processes or iSCSI sessions if killed forcefully. Embedded test certificates are static and only for local MinIO.

### Test Signals
Successful `tox` completion is the primary signal. Setup failures around instance managers, MinIO, qemu conversion, or iSCSI cleanup indicate environmental rather than unit-code failures.

## sources/control-plane/csi-driver-nfs/test/sanity/run-test.sh

Purpose: runs CSI sanity tests against a locally started `nfsplugin` process and Dockerized NFS server. It installs the CSI sanity binary, provisions a local NFS server, starts the plugin on a unix socket, and executes selected sanity cases.

Important flow: `cleanup` kills `nfsplugin`, removes `csi-test`, and deletes Docker container `nfs`. `install_csi_sanity_bin` clones `kubernetes-csi/csi-test` v5.4.0 into GOPATH with modules disabled and runs `make install`. `provision_nfs_server` installs `nfs-common` and runs `itsthenetwork/nfs-server-alpine`.

State includes GOPATH source checkout, Docker container `nfs`, `nfsshare` directory, `/tmp/csi.sock`, and a background plugin process. Dependencies include apt, Docker, git, make, local `bin/nfsplugin`, and csi-sanity. Risks include `pkill -f nfsplugin` killing unrelated processes, unpinned Docker image `latest`, root package installation, and skipped sanity cases masking unsupported idempotency/capability paths. Test signal is CSI interface-level sanity coverage.

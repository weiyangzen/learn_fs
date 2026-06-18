# sources/cloud-native/ostree/tests/test-admin-deploy-emptyetc.sh

Purpose: tests deployment when the committed tree contains an empty `/etc`, ensuring defaults from `/usr/etc` still populate the mutable deployment etc.

Important APIs/functions: `setup_os_repository`, direct mutation of `${test_tmpdir}/osdata`, `ostree commit`, `pull-local`, `ostree admin deploy`, `admin --print-current-dir`, and file content assertions.

Control flow: creates an empty `etc` directory in the source tree, commits it, pulls the runtime, deploys, resolves the current deployment path, and checks `etc/NetworkManager/nm.conf` contains the default daemon file.

State/persistence: updates the test OS repository and writes deployment `/etc`. Dependencies include the harness-created `/usr/etc/NetworkManager/nm.conf`.

Integration/risk/test signals: protects `/usr/etc` to `/etc` merge behavior when `/etc` exists but is empty. One TAP case reports `empty etc`.

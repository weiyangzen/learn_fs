# sources/cloud-native/ostree/tests/test-admin-gpg.sh

Purpose: validates admin deploy/status behavior for GPG-signed commits pulled over HTTP.

Important APIs/functions: custom `setup_os_repository_signed()` builds a signed OS repo using `--gpg-sign` and `--gpg-homedir`; uses `ostree remote add`, `pull-local --gpg-verify=true`, `admin deploy`, `admin status`, and `admin status --verify`.

Control flow: skips without `OSTREE_HTTPD`, creates signed runtime/devel commits and HTTP serving symlink, initializes sysroot and bootloader, adds remote, pulls with verification, deploys, and checks status output includes valid GPG signature information without missing-key errors.

State/persistence: creates signed repo objects, commitmeta signatures, HTTP daemon state, sysroot deployments, and bootloader assets. Dependencies include gpgme, test gpghome, and HTTP test server.

Integration/risk/test signals: bridges repository signing with admin status verification. Risks include GPG environment brittleness and exact status text. Two TAP cases cover deploy and signature display.

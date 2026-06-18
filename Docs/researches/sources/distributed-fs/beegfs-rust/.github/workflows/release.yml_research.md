<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.github/workflows/release.yml -->
## sources/distributed-fs/beegfs-rust/.github/workflows/release.yml

**Purpose:** Release workflow that builds packages, signs the checksum file, and creates or updates a GitHub release.

**Important APIs/types/functions:** Triggers manually or on tags matching `v*.*.*`. Uses contents write permission, `CARGO_LOCKED=1`, checkout with tags, local package composite action, `crazy-max/ghaction-import-gpg`, manual `gpg --detach-sign`, and `ncipollo/release-action`.

**Control flow:** The workflow checks out full history, runs `.github/actions/package`, imports the package-signing GPG key from secrets, signs `target/package/checksums.txt`, then uploads RPMs, DEBs, checksums, and the signature to a non-draft release with generated notes, replacing artifacts on unreleased updates.

**State and persistence behavior:** Writes release artifacts under `target/package` and publishes them to GitHub Releases. Secrets provide GPG key material and passphrase.

**Dependencies and integration points:** Depends on the composite package action, Makefile package target, Cargo packaging metadata in `mgmtd/Cargo.toml`, and repository secrets `PUBLICREPO_GPGPACKAGEKEY` and `PUBLICREPO_GPGPACKAGEPASSPHRASE`.

**Risks:** GPG passphrase is passed in a shell command; GitHub masks secrets, but command-line exposure on the runner is still a consideration. Tag pattern is broad and trusts semantic-looking `v*.*.*` tags. A failed package action prevents release publication; a failed signing step leaves built artifacts unpublished.

**Test signals:** Dry-run through `workflow_dispatch` on a test tag or fork, verify artifact names, checksum signature, generated release notes, and behavior when updating an existing unreleased release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.github/workflows/release.yml -->

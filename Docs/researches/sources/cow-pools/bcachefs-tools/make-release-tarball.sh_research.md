# File Research: sources/cow-pools/bcachefs-tools/make-release-tarball.sh

## Purpose
Manual release script for producing and publishing bcachefs-tools source tarballs.

## Workflow
- Checks out tag `v$version`.
- Cleans the tree and runs `make generate_version`.
- Generates Rust dependency license text with `cargo license`.
- Creates `bcachefs-tools-$version.tar` from git-tracked files plus generated `version.h` and license file.
- Compresses with `zstd --ultra`.
- Produces detached and clear-signed GPG signatures.
- Uploads artifacts to `evilpiepirate.org`.
- Runs `cargo-vendor-filterer`.
- Creates `.cargo/config.toml` pointing crates.io and a custom bindgen git source to `vendor`.
- Builds and publishes a vendored tarball variant.

## Dependencies
Requires git, make, cargo license, zstd, gpg, scp, and cargo-vendor-filterer.

## Notes
The script assumes release infrastructure paths and GPG identity are already configured locally.

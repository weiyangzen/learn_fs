# sources/compression/zstd/.github/workflows/publish-release-artifacts.yml

Purpose: release-published workflow that creates signed and checksummed source archives and uploads them as GitHub release assets.

Important behavior: it runs only for published releases and tag refs. The archive step derives `TAG` from `GITHUB_REF`, maps `vX.Y.Z` to artifact version `X.Y.Z`, creates `zstd-$VERSION.tar` via `git archive`, compresses it with `zstd -19` and `gzip -9`, computes SHA256 files, and optionally imports a GPG key from secrets to create detached armored signatures. The publish step uses `skx/github-action-publish-binaries` with `GITHUB_TOKEN` to upload `artifacts/*`.

State, dependencies, and integration: depends on Git, zstd/gzip/sha256sum/gpg on the Ubuntu runner, release secrets, and GitHub release permissions. Artifacts are generated in an `artifacts` subdirectory.

Risks and test signals: secret handling and tag parsing are critical. The workflow assumes a `zstd` binary is available on the runner. Validation is mostly by successful release upload; release_check/manual workflows provide complementary pre-release signals.

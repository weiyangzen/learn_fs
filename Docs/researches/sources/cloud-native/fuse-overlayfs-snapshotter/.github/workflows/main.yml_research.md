<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/main.yml -->
# sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/main.yml

Purpose: primary CI workflow for the containerd fuse-overlayfs snapshotter.

Important jobs: project checks run containerd project checks with Go 1.24; linters run golangci-lint; test builds and runs `make test` against matrixed fuse-overlayfs versions `v1.0.0`, `v1.13`, and `main`; cross builds release artifacts through `make artifacts`.

State and integration: runs on GitHub Actions for pushes, PRs, and manual dispatch. It uses Docker/buildx and rootless/FUSE test containers via the Makefile. Risks include dependence on building external fuse-overlayfs commits, Docker-in-CI capabilities, and version matrix drift. Test signal is strong CI coverage for project hygiene, linting, snapshotter test suite, and cross compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/main.yml -->

# sources/cloud-native/cri-o/Makefile

Purpose: central build, install, verification, documentation, mock generation, release, and CI command contract for CRI-O.

Important APIs and control flow: defines Go commands, build tags, install prefixes, build output directories, tool versions, linker metadata, and helper macros. Build targets create `bin/crio`, `bin/pinns`, test binaries, static Nix builds, cross binaries, metrics exporter, generated `crio.conf`, manpages, completions, and docs. Install targets lay binaries, manpages, completions, systemd units, CRI-O config, oci-umount config, and crictl config into prefix paths. Verify targets run golangci-lint, shellcheck, shfmt, NRI Bats, vendor checks, Ginkgo unit tests with coverage, local integration tests, dependency validation, gosec, govulncheck/VEX, mdtoc, prettier, docs validation, log capitalization, and config-template validation. Utility targets update vendoring, Nix flake, mocks, release notes, dependencies, releases, tag reconciliation, artifact uploads, and OCI artifacts.

State and persistence: writes under `bin/`, `build/`, generated docs, `crio.conf`, vendored modules, mocks, and install destinations. `clean` removes generated local artifacts.

Dependencies and integration: integrates Go, Nix, container runtime, system tools, scripts under `hack/` and `scripts/`, Ginkgo, mockgen, go-md2man, security tools, and CI workflows.

Risks: many targets download tools at execution time. Generated-file targets depend on clean-tree checks in CI. Privileged/static build targets can modify `/nix` or require container privileges.

Test signals: most GitHub workflows delegate to this file, making target success the core build and verification signal.

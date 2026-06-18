# sources/cloud-native/soci-snapshotter/.github/workflows/prebuild.yml

Purpose: pre-build quality gates for metadata, secrets, lint, YAML, shell scripts, and config generation.

Important APIs/types/functions: jobs `check`, `git-secrets`, `lint`, `yamllint`, `shellcheck`, and `config`; installs flatc binary and check tools; runs `check-ltag`, `check-dco`, `check-flatc`, git-secrets scan-history, golangci-lint in `.` and `cmd`, `yamllint .`, shellcheck in a container, and `make && ./scripts/check-config.sh`.

Control flow: triggered on main/release pushes and PRs. Jobs run independently on Ubuntu except shellcheck container.

State and persistence: no repository persistence; scans commit history and generated config in workspace.

Dependencies/integration: depends on script suite, `.golangci.yml`, `.yamllint.yml`, git-secrets repo, flatbuffers release artifact, and Makefile.

Risks: shell glob `. /**/*.sh` style may miss root-level scripts depending on shell behavior, though container shell likely expands recursive glob. Secret scan history can be slow.

Test signals: CI job statuses across lint/security/config gates.

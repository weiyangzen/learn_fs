# sources/cloud-native/cri-o/.github/workflows/nixpkgs.yml

Purpose: monthly automation to update Nix flake/package inputs for CRI-O.

Important jobs and flow: runs manually or on the first day of each month. On the canonical `cri-o/cri-o` main branch, it checks out code, installs Nix, runs `make nixpkgs`, detects a non-empty git diff, and opens a signed PR on branch `nixpkgs` with labels `kind/ci`, `release-note-none`, and `ok-to-test`.

State and persistence: modifies flake-related files when updates exist and creates a PR; otherwise no persistent change.

Dependencies and integration: uses Cachix Nix installer and peter-evans/create-pull-request. Relies on `Makefile` target `nixpkgs`.

Risks: scheduled dependency drift can break static builds. Permissions allow content and PR writes only in the guarded canonical repo.

Test signals: generated PR plus downstream `test` workflow static build lanes validate the update.

# File Research: sources/cow-pools/bcachefs-tools/.github/workflows/nix-flake-update.yml

- GitHub Actions workflow named `update-flake-lock`.
- Runs manually, monthly, and when `flake.nix` changes.
- Installs Nix with a GitHub token and delegates lockfile updates to `DeterminateSystems/update-flake-lock@v21`.

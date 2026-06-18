# File Research: sources/cow-pools/bcachefs-tools/.github/workflows/nix-flake.yml

- CI workflow for pull requests and pushes.
- First job evaluates `.#githubActions.matrix` with Nix and exports it as a GitHub Actions matrix.
- Second job builds each matrix attr via `nix build -L`.

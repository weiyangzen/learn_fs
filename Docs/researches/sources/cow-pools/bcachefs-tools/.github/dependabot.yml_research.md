# File Research: sources/cow-pools/bcachefs-tools/.github/dependabot.yml

This is a minimal Dependabot configuration for GitHub Actions dependency updates. It uses Dependabot config version 2, watches the repository root, and schedules weekly update checks for workflow action versions.

Integration role: keeps `.github/workflows/*` action pins current. It does not cover Rust crates, Nix inputs, Debian dependencies, or other package ecosystems.

Risk/maintenance notes: the scope is intentionally narrow; workflow action drift is automated, but Cargo/Nix updates are handled elsewhere.

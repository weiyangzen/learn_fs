# sources/cloud-native/composefs/deny.toml

Purpose: cargo-deny policy for Rust dependency license/source hygiene in the composefs repository.

Important APIs/types/functions: denies unlicensed crates, allows Apache/MIT/BSD/Unicode licenses, denies unknown registries and unknown git sources, and allows no git sources.

Control flow: cargo-deny reads this to evaluate dependency graph compliance.

State/persistence: policy file only.

Dependencies/integration: cargo-deny and any Rust components in the repo.

Risks/test signals: allowlist may need updates for new transitive licenses. No bans are configured, so duplicate/vulnerable crate policy may be elsewhere or absent.

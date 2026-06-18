# sources/cloud-native/ostree/deny.toml

Purpose: cargo-deny policy for Rust dependency license/source validation inside the ostree tree.

Important APIs/types: `[licenses]` allow list for Apache, MIT, BSD, Unlicense, and Unicode licenses; `private = { ignore = true }`; `[sources]` policy denying unknown registries and unknown git sources with no git allowlist.

Control flow: declarative config consumed by `cargo deny`; it permits only listed licenses and requires dependency sources to be known/approved.

State and persistence: no runtime state; it controls CI/policy results.

Dependencies and integration: integrates Rust dependency audits with repository CI. It is relevant for Rust subcomponents and vendored/transitive crates.

Risks and test signals: risks include new dependencies with unlisted licenses, private crate handling hiding policy checks, and git dependencies being rejected unless explicitly allowed. Signal is a successful `cargo deny check` in the Rust workspace.

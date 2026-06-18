<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/deny.toml -->
# sources/cloud-native/nydus/deny.toml

## Purpose

This file configures `cargo deny` policy for the Rust workspace, covering advisory handling, license allowlists, duplicate-version warnings, and allowed crate sources.

## Important APIs, Types, and Functions

Sections include `[graph]`, `[advisories]`, `[licenses]`, `[[licenses.clarify]]`, `[licenses.private]`, `[bans]`, and `[sources]`. Advisory ignores document current accepted risks for bincode, rand, ring, rsa, rustls-pemfile, hickory-proto, rustls-webpki, and proc-macro-error2. License policy allows common permissive licenses and clarifies `ring` as `ISC AND MIT AND OpenSSL`.

## Control Flow

`cargo deny check` reads this declarative policy and applies lint levels. Yanked crates warn, multiple versions warn, wildcard dependencies are allowed, unknown registries/git repositories warn, and crates.io is the allowed registry.

## State and Persistence Behavior

The file has no runtime state, but it persists the repository's dependency risk posture. Advisory ignore reasons are durable audit records and must be kept current as dependencies change.

## Dependencies and Integration Points

It integrates with CI or local `cargo deny` runs and the RustSec advisory database. It affects all Rust crates in the Nydus workspace, including `nydus-rafs`.

## Risks and Test Signals

Ignored advisories can mask real exposure if dependency usage changes. Several ignores cite transitive dependencies and no safe upgrades, so periodic review is essential. The policy currently warns rather than denies for yanked, duplicate, unknown source, and unknown git conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/deny.toml -->

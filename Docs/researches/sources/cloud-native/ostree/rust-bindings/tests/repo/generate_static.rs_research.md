# sources/cloud-native/ostree/rust-bindings/tests/repo/generate_static.rs

Purpose: This test verifies static delta generation through the safe Rust repo wrapper.

Important APIs, types, and functions: `should_generate_static_delta_at` builds a `HashMap<String, glib::Variant>` with a `filename` option, encodes a NUL-terminated path as a variant, creates two commits, and calls `Repo::static_delta_generate` with `StaticDeltaGenerateOpt::Major`, `Some(&from)`, `&to`, no metadata, option variant, and no cancellable.

Control flow: Create a temp output path, convert it to the variant format expected by libostree, create a temporary repo, commit two revisions, invoke static delta generation, then assert that the target delta file exists.

State and persistence behavior: Writes two temporary commits and a static delta file under a temporary directory. No persistent repo mutation survives outside test cleanup.

Dependencies and integration points: Depends on GLib variant conversion traits, the safe `ostree` repo API, `TestRepo`, and libostree's static delta backend.

Risks: The path conversion requires valid UTF-8 and successful `CString` creation. The test only checks file existence, not delta contents, signature validation, or apply behavior.

Test signals: Passing indicates the Rust wrapper can marshal static delta options and invoke libostree to write a delta artifact.

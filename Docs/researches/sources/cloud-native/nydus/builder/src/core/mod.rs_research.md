# sources/cloud-native/nydus/builder/src/core/mod.rs

Purpose: module declaration hub for the builder core.

Important APIs/types/functions: declares private core submodules: `blob`, `bootstrap`, `chunk_dict`, `context`, `feature`, `layout`, `node`, `overlay`, `prefetch`, `tree`, `v5`, and `v6`.

Control flow: no runtime flow. Rust module loading compiles these files as the internal builder core namespace.

State and persistence: none directly. Stateful behavior lives in declared modules such as `context`, `blob`, `bootstrap`, and `tree`.

Dependencies and integration points: controls visibility boundaries with `pub(crate)` modules. The crate root or parent modules can re-export selected items while keeping implementation details internal to the crate.

Risks: adding a new core file requires declaration here. Because all modules are crate-visible rather than public API, external crates should not depend on these paths directly.

Test signals: no tests in this file; compilation validates that declared modules exist and their internal references resolve.

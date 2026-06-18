# sources/control-plane/mayastor/sysfs/Cargo.toml

Purpose: crate manifest for a small `sysfs` helper library, version `1.0.0`, edition 2018.

Important APIs/types/functions: no dependencies are declared, so the crate uses only Rust standard library.

Control flow: none; Cargo metadata only.

State/persistence: none directly.

Dependencies/integration: workspace utility crate for reading/writing sysfs-style files.

Risks: minimal; dependency-free crate should remain portable.

Test signals: compile checks confirm manifest and library remain valid.

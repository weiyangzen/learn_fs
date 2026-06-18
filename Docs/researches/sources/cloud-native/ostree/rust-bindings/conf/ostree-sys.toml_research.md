# sources/cloud-native/ostree/rust-bindings/conf/ostree-sys.toml

Purpose: This GIR configuration generates the low-level `ostree-sys` Rust FFI crate for OSTree 1.0.

Important settings: `work_mode = "sys"`, `library = "OSTree"`, `version = "1.0"`, `target_path = "../sys"`, and `single_version_file = true`. External libraries are GLib, GObject, and Gio. `girs_directories` points to `../gir-files`.

Control flow and state: This file is consumed by `gir` from the Makefile and controls which raw C symbols/types become Rust FFI. It writes generated sys bindings under `../sys` and does not execute runtime logic.

Dependencies and integration points: Integrates the OSTree GIR file with gtk-rs sys generation and links through GLib/GObject/Gio FFI crates. The normal binding config depends on the generated sys layer.

Risks: The ignore list removes private, version-dependent, and build-dependent symbols such as private stream classes, signing subclasses, and version constants. If a symbol moves from private to public or vice versa, the sys surface can become incomplete or expose unsupported API. Ignoring build-dependent constants avoids unstable bindings but means callers need other ways to query features.

Test signals: Regenerating sys bindings and compiling downstream `ostree` Rust bindings is the main test. ABI/link tests should catch missing symbols, while GIR report review should catch newly exposed private APIs.

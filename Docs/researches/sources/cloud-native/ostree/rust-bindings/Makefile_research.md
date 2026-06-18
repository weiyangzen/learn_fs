# sources/cloud-native/ostree/rust-bindings/Makefile

Purpose: This Makefile orchestrates generation of Rust bindings from GIR metadata, fetching GIR inputs, and merging LGPL documentation into vendored docs.

Important targets and variables: Variables pin `GIR_REPO`, `GIR_VERSION`, `GIR_FILES_VERSION`, `OSTREE_REPO`, `OSTREE_VERSION`, and `RUSTDOC_STRIPPER_VERSION`. `all` runs `gir`. `target/tools/bin/gir` installs gtk-rs `gir` at a pinned revision. `gir` runs generation with `conf/ostree-sys.toml` and `conf/ostree.toml`. `gir-report` runs `gir -m not_bound`. `merge-lgpl-docs` installs `rustdoc-stripper`, runs gir doc mode, and writes `target/vendor.md`. `update-gir-files` refreshes GLib/Gio/GObject/GModule GIR files and symlinks local `OSTree-1.0.gir`.

Control flow and state: Persistent/generated state includes `target/tools`, downloaded `gir-files/*.gir`, symlinked `gir-files/OSTree-1.0.gir`, generated Rust binding code, and `target/vendor.md`.

Dependencies and integration points: Depends on Cargo install, curl, gtk-rs/gir, rustdoc-stripper, upstream GIR files, and a local OSTree GIR file. It is the bridge between libostree introspection metadata and the generated `src/auto` modules.

Risks: Pinned generator versions improve reproducibility but can lag new GIR features. Network fetches can fail or change availability. Regeneration can cause broad diffs in generated files, so commits should separate generator updates from manual wrapper changes.

Test signals: `make gir` should be clean or produce expected diffs; `make gir-report` should identify intended not-bound APIs; CI feature tests should compile the regenerated bindings.

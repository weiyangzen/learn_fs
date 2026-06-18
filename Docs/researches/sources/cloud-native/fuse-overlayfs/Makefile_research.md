<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/Makefile -->
# sources/cloud-native/fuse-overlayfs/Makefile

Purpose: local build, test, install, and cleanup automation for the Rust fuse-overlayfs binary.

Important targets: `build` runs Cargo release build; `unit-test` runs release-mode Cargo tests; `integration-test` requires root, then runs a fixed list of shell integration tests with the built binary on PATH; `test-single` runs one integration script; `test` combines unit and integration; `install` installs the release binary; `clean` runs Cargo clean.

State and integration: writes Cargo target artifacts, installs to `$(DESTDIR)$(BINDIR)` when requested, and runs root/FUSE integration scripts. Risks include integration tests requiring root and host FUSE setup, release-mode tests taking longer, and `CARGO_HOME` defaulting to a repo-local `.cargo`. Test signal is explicit unit and integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/Makefile -->

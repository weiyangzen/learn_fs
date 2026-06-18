<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/Makefile -->
## sources/cloud-native/ostree/tests/kolainst/Makefile

Purpose: installs kola external test assets and Rust installed-test binary into the coreos-assembler kola layout.

Important targets: `all` syntax-checks top-level shell scripts and generates `destructive-list.txt` by running `cargo run --release -- list-destructive`; `install` copies shell libraries/directories, installs `ostree-test`, installs destructive ignition stamp config, and calls `install-wrappers.sh`; `localinstall` installs into `../kola`.

Control flow/state: uses `find`, `ls`, `rsync`, and `install`. It writes generated wrapper tests into the target tree.

Dependencies/integration: depends on the Rust `inst` binary and coreos-assembler's `/usr/lib/coreos-assembler/tests/kola/ostree/` layout.

Risks/test signals: `LIBSCRIPTS := $(shell ls *.sh)` is simple and shell-sensitive. Successful install should produce nondestructive-rs data and per-destructive wrapper scripts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/Makefile -->

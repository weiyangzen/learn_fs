# sources/cloud-native/ostree/tests/runkola

Purpose: developer helper to build the project, create a QEMU image through CoreOS-style tooling, install kola tests, and run kola integration tests.

Important APIs/functions: uses `git rev-parse --show-toplevel`, `make`, `cosa build-fast`, `make -C tests/kolainst`, `sudo make -C tests/kolainst install`, and `kola run -p qemu --qemu-image`.

Control flow: moves to the repository root, builds, selects the first `fastbuild-*-qemu.qcow2`, defaults the test pattern to `ext.ostree.*` if no arguments are provided, installs test assets, and `exec`s kola.

State/persistence: creates build outputs, QEMU images, and installed kola tests. It depends on `cosa`, `kola`, sudo, and a QEMU-capable host.

Integration/risk/test signals: bridges local source builds to VM-level validation. Risks are destructive or expensive host-side build/install steps and ambiguous image selection. Success is kola's exit status after replacing the shell process.

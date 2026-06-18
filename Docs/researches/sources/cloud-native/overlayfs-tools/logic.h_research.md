# sources/cloud-native/overlayfs-tools/logic.h

Purpose: declares the high-level overlay action functions used by the `overlay` CLI.

Important APIs/types/functions: extern flags `verbose`, `brief`, and `use_rsync`; functions `vacuum`, `diff`, `merge`, and `deref`.

Control flow: callers pass lower/upper or mount/upper directories and optional script stream. Functions return zero on success and nonzero on fatal traversal or unsupported input.

State and persistence: actions may write scripts or stdout output; filesystem mutations only happen if generated scripts are later executed.

Dependencies/integration: consumed by `main.c`, implemented by `logic.c`.

Risks: comments still say “three feature functions” though four are declared. Global flags make concurrent independent runs impossible.

Test signals: CLI tests exercise the exported actions through `overlay`.

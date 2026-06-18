# sources/cloud-native/overlayfs-tools/logic.c

Purpose: implements the `overlay` command actions `vacuum`, `diff`, `merge`, and `deref` by traversing an upperdir and comparing or transforming it relative to a lowerdir or mounted overlay view.

Important APIs/types/functions: xattr probes `is_opaque`, `is_redirect`, `is_metacopy`, `is_opaquedir`; comparison helpers `regular_file_identical` and `symbolic_link_identical`; traversal callbacks for vacuum/diff/merge/deref; generic `traverse`; public `vacuum`, `diff`, `merge`, and `deref`.

Control flow: `traverse` walks upperdir with FTS, maps each upper path to corresponding lower/mount path, stats lower, dispatches by file type, and allows callbacks to skip subtrees. Diff prints added/removed/modified/replaced entries. Vacuum emits shell commands to remove upper copies identical to lower. Merge emits commands to move/copy/remove lower and upper content. Deref emits commands to replace redirect/metacopy entries with real mounted content.

State and persistence: direct execution is avoided here; it writes shell commands to a script stream or prints diff output. Later `main.c` may execute generated scripts with `--force`.

Dependencies/integration: uses trusted overlay xattrs, FTS, shell command generation in `sh.c`, and global formatting flags.

Risks: redirect merge is intentionally unsupported and aborts. Special files generally fail. File content comparison uses stack buffers sized from filesystem block size. Diff semantics around opaque directories and brief/verbose modes are subtle.

Test signals: Meson test fixtures compare diff output in normal, verbose, and brief modes; additional tests should execute generated vacuum/merge/deref scripts on controlled overlays.

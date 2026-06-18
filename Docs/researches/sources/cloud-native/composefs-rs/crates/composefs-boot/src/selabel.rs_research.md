# sources/cloud-native/composefs-rs/crates/composefs-boot/src/selabel.rs

## Purpose
This module applies target SELinux file labels to an in-memory composefs tree. It reads SELinux policy files from either the composefs repository or an on-disk root directory, builds a regex automaton for `file_contexts`, applies substitutions, and writes or removes the `security.selinux` xattr on directories and leaves.

## Important APIs, types, and functions
`XATTR_SECURITY_SELINUX` is the xattr key. `process_spec_file` parses `file_contexts`, `file_contexts.local`, and `file_contexts.homedirs` lines into regex patterns and context strings, including optional file-type filters. `process_subs_file` parses alias mappings from `.subs` files.

`Policy` owns substitution aliases, a lazy DFA, cache, and context list. `Policy::build_from` loads mandatory `file_contexts`, optional extension files, reverses rule order to preserve last-match semantics, and builds a `regex_automata` DFA. `lookup(path, ifmt)` matches path plus SELinux file-type code and returns the selected context unless it is `<<none>>`.

`open_file` reads policy files from composefs inline or external objects. `selabel(fs, repo)` reads policy from the image tree. `selabel_from_dir(fs, rootfs)` reads policy via `openat` from an on-disk root. `build_policy`, `apply_policy`, `strip_selinux_labels`, `relabel`, and `relabel_dir` implement the shared flow.

## Control flow
The public functions first locate `/etc/selinux/config`. If it is absent or lacks `SELINUXTYPE`, all existing SELinux labels are stripped and `false` is returned. If a policy exists, the code loads policy files under `<policy>/contexts/files`, builds the DFA, and recursively walks the filesystem from `/`. For each path it applies any substitution, determines the file-type code, looks up a label, and updates xattrs.

## State and persistence behavior
The module mutates the `FileSystem` in place. Directory stats are relabeled directly. Leaf stats are relabeled through the leaves table. To handle hardlinks, `relabel_dir` tracks labels already committed for each `LeafId`; if another path to the same leaf needs a different label, the leaf is cloned, the directory entry is remapped to the clone, and the new label is applied independently. If no policy is available, all `security.selinux` xattrs are removed.

## Dependencies and integration points
It depends on composefs tree, repository, and dumpfile/test helpers; `regex_automata` for matching; `rustix` for fd-relative policy reads; and `anyhow` plus `fn_error_context` for diagnostics. `lib.rs` calls it during boot transforms. The `composefs-ctl` bootable paths rely on it to ensure the generated root image has target labels, not build-host labels.

## Risks
SELinux regex compatibility is not full PCRE compatibility, so unusual distro policy expressions could mismatch. `process_spec_file` uses whitespace splitting, which may reject or misparse contexts with unexpected whitespace. DFA cache size is fixed at 10 MB. The hardlink-breaking behavior is necessary for correctness but changes deduplication and leaf identity. Substitutions are applied once at directory entry traversal, so subtle differences from libselinux behavior are possible.

## Test signals
Tests build synthetic filesystems with embedded policies and cover normal labeling, no-policy stripping, type-specific labels, `.subs` aliases, `<<none>>`, `.local` overrides, devices and FIFOs, stale label replacement, and hardlink splitting for paths requiring different labels. One test asserts no hardlinks remain in a bootable-layout scenario with cross-domain license-file hardlinks.

# sources/distributed-fs/ceph-client/scripts/setlocalversion

Purpose: `setlocalversion` computes the kernel release suffix by combining `KERNELVERSION`, `localversion*` files, `CONFIG_LOCALVERSION`, `LOCALVERSION`, and optional Git-derived SCM state.

Important APIs, types, and functions: `try_tag()` accepts annotated tags that are ancestors of HEAD and records commit count. `scm_version()` emits `+`, `-NNNNN-g<12hex>`, and optionally `-dirty` depending on tag distance and repository state. `collect_files()` concatenates localversion files while ignoring backup names containing `~`.

Control flow: the script parses `--no-local` and optional source tree, requires `KERNELVERSION`, collects build-tree and source-tree localversion fragments, and either emits a no-local version or validates `include/config/auto.conf`. It extracts `CONFIG_LOCALVERSION`, uses `CONFIG_LOCALVERSION_AUTO` to decide full SCM suffix behavior, and prints the final release string.

State and persistence: it only reads files and Git metadata. It deliberately avoids Git commands that create index locks when checking dirty state.

Dependencies and integration points: heavily used by Kbuild to produce `kernelrelease`. Depends on Git when SCM suffixes are needed, `sed`, `grep`, and `include/config/auto.conf`.

Risks: output changes affect module install paths, package names, and ABI labels. Dirty detection can be misleading on older Git fallback because `git diff-index` does not refresh the index. Annotated tag selection must preserve mainline, stable, linux-next, and RT conventions.

Test signals: test at exact tags, ahead of tags, dirty trees, absent Git metadata, separate object/source trees, `LOCALVERSION` set/empty/unset, and `--no-local`.

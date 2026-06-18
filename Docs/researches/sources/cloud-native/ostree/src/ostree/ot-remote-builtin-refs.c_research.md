# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-refs.c

Purpose: implements `ostree remote refs`, listing refs advertised by a remote, with optional revisions.

Important APIs/functions: `ot_remote_builtin_refs()` parses `--revision/-r` and `--cache-dir`, optionally calls `ostree_repo_set_cache_dir()`, fetches refs via `ostree_repo_remote_list_refs()`, sorts keys, and prints `remote:ref` or `remote:ref<TAB>rev`.

Control flow: parse/open repo, validate remote name, set cache dir if requested, fetch refs into a hash table, sort ref names with `strcmp`, print.

State/persistence: read-only with respect to repository config, but remote fetch/listing may populate or read network cache under the configured cache directory.

Dependencies/integration: libostree remote ref listing and cache directory API; GLib `GHashTable`/`GList`.

Risks: network/cache failures surface through libostree. Sorting only keys means duplicate names are impossible by hash table contract. `--revision` output format includes a tab and may be parsed by scripts.

Test signals: broader tree contains remote refs tests; not directly in this subset. Pull/admin tests indirectly rely on remote refs being resolvable.

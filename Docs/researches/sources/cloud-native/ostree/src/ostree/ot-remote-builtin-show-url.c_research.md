# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-show-url.c

Purpose: implements `ostree remote show-url`, printing a remote's configured URL.

Important APIs/functions: `ot_remote_builtin_show_url()` opens a repo, validates `NAME`, calls `ostree_repo_remote_get_url()`, and prints the URL.

Control flow: parse/open repo, validate one argument, resolve URL, print line.

State/persistence: read-only.

Dependencies/integration: shared option parsing and libostree remote URL lookup.

Risks: errors if the remote lacks a URL, has only custom backend semantics, or is missing. Output is raw URL, suitable for scripts but may include credentials if configured.

Test signals: remote add/list tests indirectly verify URLs; direct show-url coverage likely exists outside this subset.

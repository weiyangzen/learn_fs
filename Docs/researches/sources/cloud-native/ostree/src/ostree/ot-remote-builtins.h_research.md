# sources/cloud-native/ostree/src/ostree/ot-remote-builtins.h

Purpose: declares all `ostree remote` subcommand entry points.

Important APIs/types/functions: includes `ot-main.h`, wraps declarations in `G_BEGIN_DECLS`/`G_END_DECLS`, and uses `BUILTINPROTO(name)` to declare the standard builtin signature for add, delete, GPG, list, show-url, refs, summary, and HTTP-cookie commands.

Control flow/state: no runtime flow or persistent state. Conditional declarations for cookie commands depend on `HAVE_LIBCURL_OR_LIBSOUP`.

Dependencies/integration: consumed by `ot-builtin-remote.c` and each remote subcommand implementation. It standardizes signatures so they can be placed in `OstreeCommand` tables.

Risks: conditional prototypes must match build-system conditional sources; mismatch can cause compile/link failures. Command names such as `list_gpg_keys` map to hyphenated CLI names in the command table elsewhere.

Test signals: compile coverage plus all remote command integration tests.

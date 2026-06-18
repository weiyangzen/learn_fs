# sources/cloud-native/ostree/src/ostree/ot-remote-cookie-util.h

Purpose: declares cookie jar helper functions for remote cookie subcommands.

Important APIs/functions: `ot_add_cookie_at()`, `ot_delete_cookie_at()`, and `ot_list_cookies_at()` all take a directory fd, jar path, and `GError **`; add/delete also take cookie identity/value fields.

Control flow/state: no implementation. The API implies operations relative to `dfd`.

Dependencies/integration: includes `libglnx.h` for GLib/error/fd conventions and is consumed by cookie builtins.

Risks: callers expect all helpers to honor `dfd`; implementation review shows list currently does not, so the header contract is stronger than actual behavior.

Test signals: compile coverage and remote cookie integration tests.

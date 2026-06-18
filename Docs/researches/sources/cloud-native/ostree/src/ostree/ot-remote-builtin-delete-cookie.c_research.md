# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-delete-cookie.c

Purpose: implements `ostree remote delete-cookie`, removing a named cookie from a remote cookie jar.

Important APIs/functions: `ot_remote_builtin_delete_cookie()` validates `NAME DOMAIN PATH COOKIE_NAME`, derives `<remote>.cookies.txt`, and calls `ot_delete_cookie_at()` against the repository dfd.

Control flow: parse/open repo, validate four positional arguments, derive jar path, rewrite the cookie jar without matching records, and propagate any utility error.

State/persistence: rewrites the cookie jar atomically using the utility's temporary file/link replacement path. It reports an error if no matching cookie was found.

Dependencies/integration: depends on private repo dfd access and `ot-remote-cookie-util.c`.

Risks: deleting from a missing jar creates/replaces an empty jar through the utility path and then returns "Cookie not found in jar". Matching is exact on domain, path, and name only.

Test signals: expected coverage is the remote cookie integration test suite, not included in this item.

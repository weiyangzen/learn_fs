# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-add-cookie.c

Purpose: implements `ostree remote add-cookie`, adding a Netscape-format cookie record for a named remote.

Important APIs/functions: `ot_remote_builtin_add_cookie()` parses no custom options beyond the shared repo options, validates `NAME DOMAIN PATH COOKIE_NAME VALUE`, builds `<remote>.cookies.txt`, and calls `ot_add_cookie_at(ostree_repo_get_dfd(repo), ...)`.

Control flow: parse options and open repo through `ostree_option_context_parse()`, validate five positional arguments, derive the jar filename, append the cookie, and return boolean status.

State/persistence: appends to a cookie jar file under the repository directory fd. The cookie utility writes an expiration about 25 years in the future and creates the jar if missing.

Dependencies/integration: depends on `ostree-repo-private.h` for repo dfd access and `ot-remote-cookie-util.h`. The builtin is only declared when HTTP support is compiled.

Risks: remote names become filenames with a `.cookies.txt` suffix, so correctness depends on remote-name validation elsewhere. Cookie values are printed/stored verbatim by utility code and are not escaped.

Test signals: likely covered by remote cookie tests outside this exact subset, such as `tests/test-remote-cookies.sh`; this file has no local unit test section here.

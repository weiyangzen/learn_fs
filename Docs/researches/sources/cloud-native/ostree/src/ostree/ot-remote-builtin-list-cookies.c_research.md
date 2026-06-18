# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-list-cookies.c

Purpose: implements `ostree remote list-cookies`, displaying all cookies in a named remote jar.

Important APIs/functions: `ot_remote_builtin_list_cookies()` validates `NAME`, derives `<remote>.cookies.txt`, and calls `ot_list_cookies_at()`.

Control flow: parse/open repo, validate remote name, parse the cookie jar, print each parsed cookie block.

State/persistence: read-only; it reads `<remote>.cookies.txt` from the repo and writes cookie values to stdout.

Dependencies/integration: uses private repo dfd access and `ot-remote-cookie-util`.

Risks: cookie values are printed in cleartext. Missing or malformed lines are silently skipped by the parser, so list output may hide corrupt entries.

Test signals: expected integration coverage is `tests/test-remote-cookies.sh`; not directly included here.

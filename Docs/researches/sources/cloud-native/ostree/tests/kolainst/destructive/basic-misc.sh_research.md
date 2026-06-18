<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/basic-misc.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/basic-misc.sh

Purpose: small destructive installed test for OSTree CLI extension discovery.

Important APIs/functions: creates `/usr/libexec/libostree/ext/ostree-env` as a symlink to `/usr/bin/env`, invokes `ostree env`, and checks environment propagation.

Control flow/state: mutates `/usr/libexec/libostree/ext/`, writes `out.txt`, removes the extension symlink, and emits one TAP test.

Dependencies/integration: requires root, writable `/usr`, `ostree`, and `libinsttest.sh`.

Risks/test signals: the script contains an apparent typo checking `out.text` while writing `out.txt`, making the test likely fail unless a stale file exists. Intended signal is `TESTENV=foo` in extension output.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/basic-misc.sh -->

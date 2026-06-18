# sources/cloud-native/ostree/tests/test-basic-user-only.sh

Purpose: wrapper plus extra cases for `bare-user-only` repository mode.

Important APIs/functions: `setup_test_repository bare-user-only`, sources `basic-test.sh`, parses `ostree --version` as YAML, tests `pull-local`, `commit --statoverride`, metadata key validation, permissions canonicalization, hardlink pulls from bare-user, and `checkout --force-copy/--union-identical`.

Control flow: runs the shared 91-case basic suite with seven extra tests, resets repos to test rejection of setuid content and empty metadata keys, preserves group-writable files, canonicalizes world-writable dirs and file modes, validates safe hardlinking, and confirms automatic canonical permissions.

State/persistence: repeatedly recreates `repo`, `repo-input`, `files`, and checkouts. Dependencies include YAML Python module and optional user xattrs.

Integration/risk/test signals: protects the unprivileged object model that strips unsafe metadata. Risks are broad inherited state from `basic-test.sh` and feature-dependent branches. Extra `ok` lines extend the TAP plan.

# sources/cloud-native/ostree/tests/test-basic.sh

Purpose: minimal wrapper that runs the shared `basic-test.sh` suite for a privileged `bare` repository.

Important APIs/functions: sources `libtest.sh`, calls `skip_without_no_selinux_or_relabel`, sets `mode="bare"`, runs `setup_test_repository "$mode"`, and sources `basic-test.sh`.

Control flow: after environment capability checks and fixture setup, all behavior is delegated to `basic-test.sh`, which covers checkout, commit, diff, pull-local, xattrs, refs, cat, union checkout, statoverride, skip lists, and pruning.

State/persistence: creates the standard `repo`, `files`, and many temporary checkouts through the shared suite. Dependencies include the libtest harness and compatible SELinux/relabeling environment.

Integration/risk/test signals: validates the broad basic CLI contract for the canonical bare mode. Risk is inherited from the large shared script; this wrapper mainly selects mode and gating.

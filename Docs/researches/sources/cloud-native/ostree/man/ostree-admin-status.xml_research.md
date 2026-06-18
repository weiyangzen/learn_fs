# sources/cloud-native/ostree/man/ostree-admin-status.xml

Purpose: documents `ostree admin status`, which lists bootable deployments and status metadata.

Important APIs/types: options `--sysroot`, `-V/--verify`, `--json`, `-S/--skip-signatures`, `-D/--is-default`, `-v/--verbose`, and `--version`.

Control flow: reads deployment list, marks booted deployment with `*`, can verify commits/signatures, render JSON, report whether booted deployment is default, or print debug/version info.

State and persistence: read-only except for possible verification cache side effects; reports persistent deployment/origin state.

Dependencies and integration: central diagnostic surface for deploy, set-default, undeploy, upgrade, signature verification, and sysroot selection.

Risks and test signals: docs must match JSON/default string contracts because callers may script them. Signals are CLI golden output, JSON schema checks, and signature verification tests.

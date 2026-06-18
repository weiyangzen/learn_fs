# sources/cloud-native/ostree/man/ostree-admin-lock-finalization.xml

Purpose: documents `ostree admin lock-finalization`, which changes whether a staged deployment is queued for next boot.

Important APIs/types: options `--sysroot="PATH"` and `--unlock/-u`; description links semantics to `ostree admin deploy --lock-finalization`.

Control flow: requires a staged deployment; default invocation locks finalization, while `--unlock` releases it so the staged deployment can be queued.

State and persistence: mutates staged deployment finalization state in the sysroot.

Dependencies and integration: part of staged deployment flows and shutdown/finalization machinery.

Risks and test signals: race-free usage is through deploy-time locking, so docs should discourage unsafe sequencing. Signals are staged deployment tests for lock/unlock and next-boot queueing.

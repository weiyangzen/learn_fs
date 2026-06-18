# sources/cloud-native/ostree/man/ostree-admin-set-default.xml

Purpose: documents `ostree admin set-default`, which makes a deployment at a given index the default for next boot.

Important APIs/types: required `INDEX`; examples show `status`, `set-default 1`, and changed boot ordering.

Control flow: reorders or rewrites boot configuration without creating a new deployment.

State and persistence: persists bootloader/default deployment metadata.

Dependencies and integration: integrates deployment indexing, bootconfig swap, and `ostree admin status`.

Risks and test signals: risks include wrong index interpretation and bootloader mismatch. Signals are status/default tests and bootconfig verification.

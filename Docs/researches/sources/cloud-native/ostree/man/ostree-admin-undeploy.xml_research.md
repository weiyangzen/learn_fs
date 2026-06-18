# sources/cloud-native/ostree/man/ostree-admin-undeploy.xml

Purpose: documents `ostree admin undeploy`, which deletes a deployment at a given index.

Important APIs/types: required `INDEX`; examples show status before/after deletion.

Control flow: selects deployment by index and removes it from deploy/boot state.

State and persistence: deletes persistent deployment directory/metadata and updates boot configuration.

Dependencies and integration: integrates with status indexing, cleanup, pinned/retained deployment policy, and bootloader updates.

Risks and test signals: risks include deleting the wrong deployment or violating retained/pinned semantics. Signals are status after deletion, bootconfig consistency, and protected deployment tests.

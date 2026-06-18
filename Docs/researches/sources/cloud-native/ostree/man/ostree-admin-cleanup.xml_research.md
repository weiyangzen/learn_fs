# sources/cloud-native/ostree/man/ostree-admin-cleanup.xml

Purpose: documents `ostree admin cleanup`, which deletes untagged deployments and repository objects and cleans partially written sysroot state after interrupted pulls/deployments.

Important APIs/types: DocBook `refentry` with synopsis `ostree admin cleanup`, refpurpose, description, and example.

Control flow: documentation models a single no-argument command. It affects sysroot boot versions, old deployments, partial deployment state, and repository garbage.

State and persistence: describes persistent deletion of deployment/repository state.

Dependencies and integration: tied to the CLI admin cleanup implementation and cross-referenced by docs for ref deletion/pruning.

Risks and test signals: docs must match deletion semantics and safety rules. Signals are DocBook generation plus CLI tests that interrupted operations can be cleaned without removing retained deployments.

# sources/cloud-native/ostree/man/ostree-init.xml

Purpose: documents `ostree init`, which initializes a new OSTree repository.

Important APIs/types: options include repository mode selection and collection-id behavior.

Control flow: creates repository directory structure and config, choosing a storage mode such as bare, bare-user, bare-user-only, or archive.

State and persistence: writes persistent repository config, object/ref directories, and collection-id metadata if provided.

Dependencies and integration: prerequisite for commit, pull, remote, and mirror workflows; repo mode affects checkout/pull/hardlink behavior.

Risks and test signals: risks include wrong mode for intended transport/permissions and unstable collection IDs breaking P2P. Signals are repo init tests for each mode and subsequent commit/pull operations.

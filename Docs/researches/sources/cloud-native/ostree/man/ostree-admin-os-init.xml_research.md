# sources/cloud-native/ostree/man/ostree-admin-os-init.xml

Purpose: documents `ostree admin os-init` as a soft-deprecated alias for `stateroot-init`.

Important APIs/types: required `STATEROOT`; short description points users to stateroot-init docs.

Control flow: no independent semantics; command delegates/aliases to stateroot initialization.

State and persistence: same as stateroot-init, creating empty deployment state for an OS name.

Dependencies and integration: backward compatibility for older admin command naming.

Risks and test signals: docs must keep alias/deprecation status clear. Signals are CLI alias tests and matching behavior with `stateroot-init`.

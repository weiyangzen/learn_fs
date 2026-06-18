# sources/cloud-native/ostree/man/ostree-log.xml

Purpose: documents `ostree log`, which prints commit history starting at a ref or commit.

Important APIs/types: required `REF`; option `--raw`.

Control flow: resolves ref, follows parent commits, and prints checksum, date, and commit message or raw GVariant data.

State and persistence: read-only over commit metadata.

Dependencies and integration: uses rev parsing and commit object metadata; examples coordinate with commit/reset pages.

Risks and test signals: risks include raw format stability and parent traversal edge cases. Signals are log output tests for linear history and raw mode.

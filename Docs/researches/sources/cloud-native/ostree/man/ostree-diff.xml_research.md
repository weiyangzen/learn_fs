# sources/cloud-native/ostree/man/ostree-diff.xml

Purpose: documents `ostree diff`, which compares filesystem trees or commits and reports changed paths.

Important APIs/types: command synopsis includes old/new targets; options include stats/ownership/xattr-related comparison controls visible in the page.

Control flow: resolves the compared trees, walks them, and reports added/modified/deleted entries with optional metadata detail.

State and persistence: read-only over repository and/or filesystem inputs.

Dependencies and integration: integrates tree traversal, rev parsing, checkout comparisons, and diagnostics for deployments/commits.

Risks and test signals: risks include xattr/ownership comparison drift and large-tree performance. Signals are diff golden tests for add/delete/modify, metadata changes, and commit-vs-dir comparisons.

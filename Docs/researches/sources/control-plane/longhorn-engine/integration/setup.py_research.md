<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/setup.py -->
## sources/control-plane/longhorn-engine/integration/setup.py

Purpose: minimal Python packaging metadata for Longhorn integration tests.

Important APIs/types/functions: calls `distutils.core.setup` with name, version, empty `packages`, and ASL 2.0 license.

Control flow, state, and persistence: import-time setup declaration only.

Dependencies and integration points: uses `distutils`, which is legacy in newer Python distributions. It is likely consumed by tox or ad hoc integration test setup.

Risks: `packages=[]` means package discovery is disabled; this is fine for tests run from source but not for installable test libraries. `distutils` deprecation can become a portability issue.

Test signals: tox/integration test startup indirectly validates whether this packaging file is sufficient.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/setup.py -->

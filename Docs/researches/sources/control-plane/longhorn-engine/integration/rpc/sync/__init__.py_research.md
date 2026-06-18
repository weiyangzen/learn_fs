<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/sync/__init__.py -->
## sources/control-plane/longhorn-engine/integration/rpc/sync/__init__.py

Purpose: empty Python package marker for the integration RPC sync client package.

Important APIs/types/functions: none exported by this file.

Control flow, state, and persistence: no runtime behavior, no state, no persistence.

Dependencies and integration points: enables imports from `integration/rpc/sync`, especially `sync_agent_client.py`.

Risks: only packaging/import risk. Removing it can break Python 2 style or explicit package discovery assumptions in older integration test tooling.

Test signals: import-based tests for `rpc.sync.sync_agent_client` indirectly validate this file.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/rpc/sync/__init__.py -->

# sources/control-plane/longhorn-engine/integration/rpc/replica/__init__.py

Purpose: package marker for replica RPC client helpers.

Important APIs/types/functions: no direct API; `replica_client.py` provides the package's substantive client wrapper.

Control flow: no executable logic.

State and persistence behavior: no state and no persistence.

Dependencies and integration points: supports import paths such as `from replica.replica_client import ReplicaClient` under the integration RPC tree.

Risks: removal can break package imports in older tooling. Side effects added here would run for every replica client import.

Test signals: package import smoke test plus direct import of `ReplicaClient`.

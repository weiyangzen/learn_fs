# sources/control-plane/longhorn-engine/integration/rpc/instance/__init__.py

Purpose: package marker for the `instance` RPC client package. The file is empty and exists so Python can import modules under `integration/rpc/instance` in environments that still rely on regular packages rather than namespace packages.

Important APIs/types/functions: no runtime API is defined here. The exported behavior is package importability for sibling modules such as `instance_client.py`.

Control flow: no executable statements.

State and persistence behavior: no module state and no persistence.

Dependencies and integration points: integrates with Python import resolution and with callers that import `instance.instance_client` or import from the `instance` package path.

Risks: adding side effects here would change package import behavior for integration tests. Removing the file may break older tooling or tests that expect a concrete package.

Test signals: package import smoke tests should include `import instance` and `from instance.instance_client import InstanceClient` under the repository's integration RPC `PYTHONPATH`.

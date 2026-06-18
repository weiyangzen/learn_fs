# sources/control-plane/longhorn-engine/integration/rpc/process_manager/__init__.py

Purpose: package marker for process-manager RPC helpers. It enables package-style imports for the `process_manager` directory.

Important APIs/types/functions: no classes, functions, constants, or side effects are defined.

Control flow: no executable logic.

State and persistence behavior: no state and no persistence.

Dependencies and integration points: participates only in Python import resolution for `process_manager.process_manager_client`.

Risks: deleting it may break tests or tools that do not support namespace-package discovery. Adding import side effects could make process-manager client imports slower or more fragile.

Test signals: import smoke coverage should include `import process_manager` and `from process_manager.process_manager_client import ProcessManagerClient`.

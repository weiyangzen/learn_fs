# sources/distributed-fs/ceph-client/tools/objtool/weak.c

Purpose: Provides weak fallback definitions for architecture hooks so generic objtool can link when an arch does not override them.

Important APIs/types/functions: `UNSUPPORTED`.

Control flow: Weak symbols return default/no-op behavior until replaced by architecture-specific implementations at link time.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on objtool arch hook declarations and compiler weak-symbol support.

Risks: A missing arch override may silently use conservative fallback behavior.

Test signals: Link generic objtool and architecture builds; verify expected hooks are overridden.

Source coverage: researched from the complete local file (34 lines, 687 bytes).

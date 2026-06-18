# sources/distributed-fs/orangefs/src/client/sysint/pint-sysint-utils.h
## sources/distributed-fs/orangefs/src/client/sysint/pint-sysint-utils.h

**Purpose:** Declares internal helper functions shared by sysint implementation files.

**APIs and control flow:** Exposes server config retrieval/release, parent lookup, client security initialize/finalize, and `client_perf_start_rollover()`. Includes broad dependencies needed by those helpers, including PVFS types, attrs, job/BMI, cached config, perf counters, Trove, client state machine, and server config.

**State and dependencies:** This is a coupling point for sysint internals. Any includer receives state-machine and server-config definitions, which can increase rebuild scope.

**Risks and tests:** The header includes `client-state-machine.h`, while that header also includes this file, so include guards prevent recursion but the dependency cycle is delicate. Tests are compile/build oriented: all sysint sources should compile cleanly under security-enabled and security-disabled configurations, and consumers should not require hidden include order.

# sources/distributed-fs/ceph-client/include/net/netns/core.h

Purpose: Defines core networking sysctl and accounting fields stored per network namespace.

Important APIs/types/functions: `struct netns_core` stores sysctl header, socket/backlog/memory/tx hash knobs, procfs protocol in-use counters, and optional RPS default CPU mask.

Control flow: Namespace init registers sysctls and allocates optional proc/RPS fields. Core socket and networking code reads these knobs on hot paths.

State and persistence: Runtime per-net sysctl state and optional per-cpu/proc data.

Dependencies/integration: Depends on sysctl, procfs, protocol in-use accounting, cpumasks, RPS, and socket core.

Risks/test signals: Test sysctl defaults/isolation, procfs cleanup, RPS mask lifetime, hot-path cache effects, and namespace teardown.

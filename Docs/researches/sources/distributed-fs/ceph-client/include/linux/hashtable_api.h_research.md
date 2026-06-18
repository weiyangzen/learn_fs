<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hashtable_api.h -->
# sources/distributed-fs/ceph-client/include/linux/hashtable_api.h

Purpose: This one-line compatibility/export header includes `linux/hashtable.h`.

Important APIs/types/functions: It declares no independent API. Including it exposes the static hash table macros and helpers from `hashtable.h`.

Control flow, state, and persistence: None in this file; all behavior is inherited from `hashtable.h`.

Dependencies/integration: It exists for include-path compatibility with users expecting a separate hashtable API header.

Risks and test signals: The only practical risk is stale includes masking direct dependency cleanup. Build tests should ensure consumers compile and no include recursion or guard conflict occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/hashtable_api.h -->

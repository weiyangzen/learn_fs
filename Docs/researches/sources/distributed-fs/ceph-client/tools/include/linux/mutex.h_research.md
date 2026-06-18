<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/mutex.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/mutex.h

## Purpose
This is an empty compatibility header for includes of `<linux/mutex.h>` in tools code.

## APIs And Flow
It exports only an include guard. It does not define `struct mutex`, lock helpers, or debug annotations.

## State, Dependencies, Risks, Tests
There is no state. The integration point is include compatibility for code paths that do not actually use mutex APIs after preprocessing. The risk is build breakage if a consumer starts requiring kernel mutex symbols instead of using pthread or other tools locks. Test signal is all tools builds passing with no unresolved mutex references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/mutex.h -->

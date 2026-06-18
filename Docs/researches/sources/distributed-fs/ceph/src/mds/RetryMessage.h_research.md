# sources/distributed-fs/ceph/src/mds/RetryMessage.h

Purpose: provides small MDS context helpers that redispatch an MDS message after an asynchronous wait condition resolves.

Important APIs and types: `C_MDS_RetryMessage` derives from `MDSInternalContext`, stores a `cref_t<Message>`, and on `finish()` calls `get_mds()->retry_dispatch(m)`. `CF_MDS_RetryMessageFactory` captures `MDSRank*` and a message and builds new retry contexts on demand.

State and persistence: state is only the retained message reference and target MDS pointer. No persistence or external state is modified until the context finishes.

Dependencies and integration: includes `MDSContext.h`, `MDSRank.h`, and `msg/Message.h`. `ScrubStack` uses `C_MDS_RetryMessage` when remote scrub handling must wait for dirfrag unfreeze before retrying the same message.

Risks and test signals: retrying preserves the original message, so callers must ensure the wait condition eventually changes and that redispatch is idempotent. Tests should cover waits that retry scrub messages without losing source identity or causing duplicate side effects.

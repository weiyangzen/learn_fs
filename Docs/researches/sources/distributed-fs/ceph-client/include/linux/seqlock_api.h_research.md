# sources/distributed-fs/ceph-client/include/linux/seqlock_api.h

Purpose: `seqlock_api.h` is a compatibility forwarding header that includes `linux/seqlock.h`.

Important APIs/types/functions: It declares no independent symbols; all seqcount and seqlock APIs come from `seqlock.h`.

Control flow: Inclusion simply exposes the main seqlock API. There is no runtime code.

State and persistence behavior: No state is owned by this wrapper.

Dependencies and integration points: It exists to satisfy include users that refer to the API-specific header while centralizing implementation in `seqlock.h`.

Risks: Because it is only one include line, any include-order or guard behavior is inherited from `seqlock.h`. Do not add partial duplicate definitions here.

Test signals: Build include users of `seqlock_api.h`, verify no symbol duplication, and ensure API availability matches direct inclusion of `seqlock.h`.

# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-tar.c

Purpose: checks TAR rollback and suspended-mode persistence across transaction commit/abort.

Important APIs/types/functions: `test_tar()` loops inline assembly that writes SPRN_TAR before, inside, and while suspended in a transaction.

Control flow: each loop sets TAR=1, begins a transaction, repeatedly sets TAR=2 inside TM and TAR=3 while suspended, then either commits and expects TAR=3 or aborts and expects rollback to TAR=1. Encoded result values 7 and 9 are accepted.

State and persistence behavior: `num_loops` is configurable from argv; TAR is per-thread SPR state.

Dependencies and integration points: requires real HTM, ppc64le, and `SPRN_TAR`.

Risks and test signals: low iteration counts can false-pass; default is 10000. Any unexpected encoded result indicates TAR corruption.

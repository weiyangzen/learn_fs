# sources/distributed-fs/ceph-client/tools/lib/subcmd/sigchain.c

Purpose: Maintains a small stack of previous signal handlers so libsubcmd can push common handlers and later restore/chain them.

Important APIs/types/functions: `sigchain_pop()` restores the previous handler for one signal. `sigchain_push_common()` pushes a handler for `SIGINT`, `SIGHUP`, `SIGTERM`, `SIGQUIT`, and `SIGPIPE`. Internal `sigchain_push()` stores previous handlers in a dynamically grown array per signal.

Control flow: Push validates signal range, grows the per-signal stack, installs the new handler with `signal()`, stores the old handler, and increments count. Pop restores the most recent saved handler and decrements.

State and persistence: Static `signals[SIGCHAIN_MAX_SIGNALS]` stores handler stacks for the process lifetime. No persistence.

Dependencies/integration: Uses `signal.h` and `subcmd-util.h` allocation/die helpers. Pager uses it to wait for the pager then re-raise signals.

Risks: Limited to signal numbers 1-31. Uses `signal()` rather than `sigaction()`, so semantics are platform-dependent. Failed `signal()` after `ALLOC_GROW()` leaves allocated capacity. Not thread-safe.

Test signals: Push/pop multiple handlers per signal, invalid signal handling, common signal coverage, and signal delivery integration with pager.

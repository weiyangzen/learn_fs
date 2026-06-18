# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-journal.h

## Purpose
Defines the libgfchangelog journal-mode state model shared by live journal processing and historical changelog processing.

## APIs, Types, and Functions
`enum api_conn` models connected, connection-in-progress, and disconnected states. `gf_changelog_entry_t` stores queued changelog paths. `gf_changelog_processor_t` owns the queue mutex/condition, waiting flag, processor thread, and list head. `gf_changelog_journal_t` stores directory streams, tracker fd, brick path, scratch directory paths, RFC3986 table, nested history journal pointer, history scan status, spinlock, connected state, and owning xlator. `gf_changelog_history_data_t` and `gf_changelog_consume_data_t` carry history search and parallel consume work. The header declares journal callbacks via `CALLBACK`, `INIT`, `FINI`, `CONNECT`, and `DISCONNECT`.

## Control Flow, State, and Persistence
The structures separate live scratch state from historical scratch state by nesting `hist_jnl`. Directory path fields point to persistent on-disk queues: `.current` for freshly decoded files, `.processing` for files exposed to consumers, `.processed` for files marked done, and a tracker fd for iterating results. Connection state is guarded by a spinlock and accessed through `JNL_SET_API_STATE()` and `JNL_IS_API_DISCONNECTED()`.

## Dependencies and Integration
Requires pthreads, `DIR`, `PATH_MAX`, Gluster list heads, booleans, callback typedefs, and xlator types supplied through included Gluster headers. It is consumed by `gf-changelog-journal-handler.c` and `gf-history-changelog.c`, and its callback names are supplied to `gf_changelog_register()` for legacy journal consumers.

## Risks and Test Signals
Risks include shared ownership between `jnl` and `hist_jnl`, lock discipline around `connected`, and fd/dir cleanup ordering. Test signals are successful initialization/fini cycles, connection/disconnection transitions, tracker fd truncation/iteration, and nested history journal cleanup without leaks.

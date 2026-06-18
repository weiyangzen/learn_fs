# sources/distributed-fs/ceph/src/mds/events/ESession.h

Purpose: Declares the journal event for a single client session open or close.

Important APIs/types: `ESession` stores client inst, open/close flag, client map version, inode intervals to free/purge, inotable version, client metadata, and auth name. It implements encode/decode/dump/test/update_segment/replay and exposes `get_client_inst`.

Control flow: Server session handling journals opens and closes. Replay recreates session state, frees/purges inode intervals on close, and advances sessionmap/inotable state.

State and persistence behavior: Persistent payload includes session identity, metadata, auth name for reclaim, and inode cleanup intervals. `update_segment()` accounts for session-related log segment state.

Dependencies and integration points: Uses `LogEvent`, entity/session types, `interval_set`, `SessionMap`, `InoTable`, and `Server` session lifecycle.

Risks: Auth name persistence is required for session reclaim after journal recreation. Inode free/purge intervals must align with inotable version and session close order.

Test signals: Open replay with metadata/auth name, close replay with free/purge intervals, dencoder old/new compatibility, and reclaim after restart.

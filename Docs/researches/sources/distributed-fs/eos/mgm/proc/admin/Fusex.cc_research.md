# sources/distributed-fs/eos/mgm/proc/admin/Fusex.cc

Purpose: Implements the legacy opaque-parameter `fusex` admin command for inspecting and controlling the MGM FUSEX/ZMQ server state.

Important APIs/types/functions: `ProcCommand::Fusex()` supports `ls`, `conf`, `evict`, `droplocks`, and `caps`. It calls `gOFS->zMQ->gFuseServer.Print()`, adjusts client heartbeat/quota intervals and broadcast-audience controls, evicts clients by UUID and reason, drops locks by inode/pid, and prints capability state.

Control flow: Only root may execute. `conf` reads `mgm.fusex.*` opaque keys, applies provided values, reports current values when omitted, and persists selected settings under the default space. `evict` base64-decodes a reason before passing it to the FUSE server client. `droplocks` parses hex inode and decimal pid. Unknown subcommands return `EINVAL`.

State and persistence behavior: Runtime FUSEX server settings are changed in `gFuseServer.Client()`. Some configuration is persisted through `FsView::gFsView.mSpaceView["default"]->SetConfigMember()` for `fusex.bca`, `fusex.bca_match`, `fusex.hbi`, and `fusex.qti`. Eviction and lock dropping mutate active client/session state.

Dependencies and integration points: Depends on `ProcInterface`, `XrdMgmOfs`, `mgm/zmq/ZMQ.hh`, `FsView`, and common base64/string helpers. It is part of the older `ProcCommand` admin path rather than the protobuf `IProcCommand` path.

Risks: Assumes `mSpaceView["default"]` exists when persisting config. `atoi()` treats invalid numeric input as zero, which can convert bad input into "show current" behavior. Heartbeat typo in error text is harmless but visible. Root-only access is broad, and eviction/droplock actions immediately affect clients.

Test signals: Root authorization, config validation boundaries for heartbeat 1..15 and quota 1..60, persistence of broadcast and interval settings, invalid numeric strings, eviction of none/one/many clients, unknown UUID `ENOENT`, lock parsing and missing lock errors, and capability filtering with URL-unescaped filters.

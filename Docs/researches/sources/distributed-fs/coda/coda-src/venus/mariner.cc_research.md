# sources/distributed-fs/coda/coda-src/venus/mariner.cc

Purpose: implements the Mariner monitoring/control facility: Unix/TCP listener setup, per-client `mariner` vprocs, async queued writes, fetch/path/volume-state reporting, diagnostic commands, and optional 9PFS handoff.

Important APIs and flow: `MarinerInit` creates a world-accessible Unix socket when available and optional TCP listeners for service `venus`, then registers MUX callbacks. `MarinerMux` accepts clients, enforces `MaxMariners`, makes sockets non-blocking, and constructs `mariner`. `MarinerLog`, `MarinerReport`, and `MarinerReportVolState` broadcast to clients that enabled fetch logging, path reports, or volume-state reports. Each `mariner` starts a writer LWP, reads command lines with `AwaitRequest`, detects Plan 9 protocol magic and transfers control to `plan9server`, parses commands in `main`, and supports debug toggles, RPC2 tracing, COP mode changes, report subscriptions, fd/path/fid/rpc2 stats, and `VenusPrint`. Non-blocking writes are queued with a fixed queue; overflow drops messages and later reports the drop count.

State and persistence: Mariner state is transient per connection: fd, flags, uid filter, output queue, writer process, command buffer, and optional 9P server. It does not write recoverable metadata.

Dependencies and integration: depends on sockets, IOMGR/LWP, RPC2/SFTP stats, `vproc` path/fid lookup, FSDB/VDB/REALMDB, `VenusPrint`, volume-state reporting, and 9PFS integration.

Risks and test signals: risks include unsynchronized `nmariners`/queue updates, socket permissions, queue overflow semantics, command parsing truncation, TCP exposure, cleanup of writer LWP on disconnect, and 9P magic detection inside line-oriented reads. Tests should connect over Unix/TCP, toggle each subscription, verify dropped-message reporting, run `pathstat`/`fidstat`, exercise disconnect while queued writes exist, and validate 9P handoff.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/pty.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/pty.c

Purpose: implements UML `pty` and `pts` channel backends, allocating host pseudo-terminal masters for consoles and serial lines.

Important APIs/types/functions: `struct pty_chan` stores announce callback, device index, raw flag, saved terminal state, and device-name buffer. Backend callbacks are `pty_chan_init()`, `pts_open()`, `pty_open()`, and ops objects `pty_ops`/`pts_ops`. `getmaster()` scans legacy BSD pty devices.

Control flow: `pts_open()` obtains a Unix98 pty via `get_pty()`, optionally sets raw mode, records `ptsname()`, and announces it. `pty_open()` scans `/dev/pty[p-s][0-f]`, verifies the slave side is accessible, sets raw mode if requested, announces, and returns the master FD.

State and persistence: backend state is per-channel and stores only host terminal attributes/name. Host pty allocation is runtime-only.

Dependencies and integration points: depends on host pty APIs, termios/raw helpers, generic channel I/O, and line announce callbacks used by console/serial setup.

Risks: legacy pty scanning is host-distribution dependent. Device-name buffer sizing assumes limited pts path length. Raw-mode error paths must close allocated masters.

Test signals: boot with `con=pty`, `con=pts`, and `ssl=pty`; verify announced host devices work; test absence of legacy ptys; resize/input/output behavior; and raw mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/pty.c -->

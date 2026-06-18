# sources/distributed-fs/coda/coda-src/resolution/subresphase2.cc

Purpose: subordinate side of RVM directory resolution phase 2: collect the local log for the target directory and ship it to the coordinator.

Important functions: `RS_FetchLogs` translates the fid, creates a VLE list, loads the target object with a read lock, dumps the vnode's resolution log with `DumpLog`, returns byte size and entry count, and sends the buffer through `rs_ShipLogs`. `rs_ShipLogs` configures a SmartFTP `SERVERTOCLIENT` side effect over an in-memory file and waits for local completion.

Control flow and state: the function probes `RecovSubP2Begin/End`, validates the volume id, gets the object, leaves a placeholder for phase-2 semantic checks such as verifying coordinator lock and log wrap status, dumps logs, ships them, and releases objects with `PutObjects`. It reads persistent RVM vnode logs but does not mutate them.

Dependencies, risks, tests: depends on `vlist`, `operations`, `DumpLog`, RPC2/SFTP, and timing infrastructure. Risks include unimplemented semantic checks, reliance on correct caller-provided side-effect descriptor semantics, and handling empty logs/buffers. Test with directories with no log, multiple log entries, side-effect failures, invalid fid translation, and cleanup of allocated dump buffers.

# sources/distributed-fs/coda/coda-src/resolution/timing.h

Purpose: declares generic resolution timing probes and the `timing_path` class used by resolution profiling.

Important APIs/types: `tpe` stores a probe id plus `timeval`. `timing_path` owns a growable array of `tpe` entries with `insert` and `postprocess` methods. Global flags `pathtiming` and `probingon` enable probes, and `tpinfo`/`FileresTPinfo` are externally allocated timing paths. Probe constants cover regular directory resolution, client-side fetch/phase work, compensation operation execution, and file-resolution stages starting at `FILERESBASE`.

Control flow and integration: included by both coordinator and subordinate resolution modules. `PROBE(info, num)` conditionally records a probe and is intentionally cheap when disabled.

State/persistence: no persistent state; runtime profiling only. The underlying implementation is heap-based and unsynchronized. Risks include duplicated ids with `rvmrestiming.h`, macro argument evaluation, and accidental use from multiple LWPs without external locking. Test signals are ordered probe output around successful resolution and correct no-op behavior when either global flag is false or the timing-path pointer is null.

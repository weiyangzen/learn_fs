<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_sysctl.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_sysctl.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_sysctl.c_research.md`.

Purpose: registers `/proc/sys/kgnilnd` controls for administrative GNI LND diagnostics and fault handling, including manual thread pause, hardware quiesce completion, stack reset, RDMAQ throttling override, and peer up/down injection.

Important APIs/types/functions: `kgn_sysctl_data_t` stores writable values. Handlers include `proc_toggle_thread_pause()`, `proc_hw_quiesce()`, `proc_trigger_stack_reset()`, `proc_toggle_rdmaq_override()`, and `proc_peer_state()`. `kgnilnd_insert_sysctl()` registers the ctl table and `kgnilnd_remove_sysctl()` unregisters it. Stub versions are compiled when `CONFIG_SYSCTL` is absent.

Control flow: sysctl writes first pass through `proc_dointvec` or `proc_dostring`, then validate `kgnilnd_data.kgn_init == GNILND_INIT_ALL` before mutating driver state. Thread pause changes copy into `kgn_quiesce_trigger` under `kgn_quiesce_mutex` and call `kgnilnd_quiesce_wait()`. Hardware quiesce writes call `kgnilnd_quiesce_end_callback()` on device 0. Stack reset calls `kgnilnd_critical_error()` and spins until `kgn_needs_reset` clears. Peer-state writes parse `up|down nid` and call `kgnilnd_report_node_state()`.

State and persistence behavior: sysctl values live in static `kgnilnd_sysctl`; effects are live kernel state only. `rdmaq_override` converts MiB/s to bytes/s and stores `kgn_rdmaq_override` with a write barrier. The registration header pointer prevents duplicate table registration and is nulled on removal.

Dependencies and integration: depends on Linux sysctl tables, Lustre version string, GNI quiesce/reset helpers, GNI device 0 handles, LNet node-state reporting, and global LND initialization flags.

Risks: `stack_reset` is a privileged destructive test hook and can block until reset completes. `sscanf("%s %d")` into a 10-byte command buffer depends on the sysctl string length cap. Device 0 assumptions mirror other GNI stack code and must hold for multi-device changes. Admin writes during partial init return errors.

Test signals: register/unregister with and without `CONFIG_SYSCTL`, read version, toggle thread pause and confirm all threads quiesce/resume, trigger stack reset and observe flag clearing, set RDMAQ override and inspect bytes value, inject peer up/down commands including malformed strings, and verify writes before full init fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_sysctl.c -->

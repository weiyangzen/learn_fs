<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_quiesce.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_quiesce.c

**Purpose:** `sclp_quiesce.c` handles SCLP signal-quiesce events by initiating a machine shutdown/quiesce sequence.

**Important APIs and functions:** `sclp_quiesce_handler()` is the SCLP event receiver. `do_machine_quiesce()` stops secondary CPUs and loads a wait PSW at address `0xfff`. Init registers `sclp_quiesce_event` for `EVTYP_SIGQUIESCE_MASK`.

**Control flow, state, and persistence:** On a quiesce event, the handler replaces `_machine_restart`, `_machine_halt`, and `_machine_power_off` with the quiesce implementation, then calls `ctrl_alt_del()` to enter the normal reboot path. The override persists for that shutdown path so later machine operations load the quiesce PSW instead of restarting normally.

**Dependencies and integration:** It depends on SCLP event delivery, SMP stop, reboot control hooks, PSW loading, and device initcall registration.

**Risks and test signals:** Risks include quiesce events during fragile contexts, callback execution from SCLP event dispatch, and changing global machine operation hooks unexpectedly. Test signals include successful registration, event-triggered `ctrl_alt_del()`, CPUs stopped before PSW load, and no effect when no quiesce event is delivered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_quiesce.c -->

# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/aha152x_core.c

Purpose: tiny wrapper that compiles the shared AHA152X SCSI core in PCMCIA mode by defining `AHA152X_PCMCIA` and `AHA152X_STAT` before including `aha152x.c`.

Important APIs/functions: no local runtime functions. The included core provides entry points used by `aha152x_stub.c`, including probe, release, and host reset helpers.

Control flow/state: Kbuild links this translation unit into `aha152x_cs.o`; runtime behavior is in the included core plus the PCMCIA stub. State is owned by the shared core.

Dependencies/integration: depends on `aha152x.c`/`aha152x.h` and the macro environment set here.

Risks/test signals: direct inclusion means macro drift changes core behavior for this module. Test with `aha152x_cs` build/link and probe/remove/reset through the PCMCIA stub.

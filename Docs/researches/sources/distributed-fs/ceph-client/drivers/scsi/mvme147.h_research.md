# sources/distributed-fs/ceph-client/drivers/scsi/mvme147.h

Purpose: small legacy header for the MVME147 built-in SCSI driver. It supplies driver-local declarations and default queue sizing used by `mvme147.c`.

Important APIs/types/functions: declares `mvme147_detect(struct scsi_host_template *)` and `mvme147_release(struct Scsi_Host *)`, which are legacy prototypes not implemented by the current module-style `mvme147.c`. Defines default `CMD_PER_LUN` as 2 and `CAN_QUEUE` as 16 when not already provided.

Control flow: no runtime control flow. Its macros are consumed when constructing the `scsi_host_template`.

State and persistence: no state or persistence.

Dependencies and integration points: includes `linux/types.h` and relies on SCSI types being visible to includers. Integrated only by `mvme147.c` in this source subset.

Risks and test signals: stale prototypes can confuse readers and should be checked before any refactor to avoid resurrecting obsolete detect/release entry points. Compile tests on m68k validate that queue macros and declarations do not conflict with modern SCSI headers.

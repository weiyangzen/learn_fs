# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_gbl.h

Purpose: this header is the cross-file symbol contract for qedi. It declares globals and functions shared between qedi main, iSCSI transport, firmware command handling, debugfs, sysfs, and recovery code.

Important declarations: globals include `qedi_io_tracing`, `qedi_host_template`, `qedi_iscsi_transport`, `qedi_ops`, debugfs operation/file arrays, and SCSI host attribute groups. Under debugfs it exposes `qedi_do_not_recover`; without debugfs this becomes constant zero. Functions cover SQ allocation/free, login/logout/TMF/text/NOP/I/O submission, task index management, cleanup, SG unmap, ITT mapping, iSCSI/TCP error handling, connection recovery, CID lookup, device missing/available marking, MTU reset, all-connection recovery, CQE processing, cleanup-all, I/O tracing, local port ID allocation/free, and SQ clearing.

Control flow and state: the header does not execute but defines how the driver objects call into each other. It is especially important for `qedi_fw.c`, which implements many of the submission and completion functions called through libiscsi transport hooks in other files.

Dependencies and integration points: it includes `qedi_iscsi.h`, so it depends on qedi connection/endpoint command definitions. It links QED operation pointers, SCSI host template, and iSCSI transport registration with firmware-path helpers.

Risks: broad global declarations increase coupling. Signature changes need synchronized edits across multiple files. The `qedi_do_not_recover` macro fallback means code that expects a mutable flag must be aware it is compile-time disabled without debugfs.

Test signals: full qedi build with all objects, compile with and without debugfs, link-time symbol resolution, and runtime coverage of each transport callback that crosses this header boundary.

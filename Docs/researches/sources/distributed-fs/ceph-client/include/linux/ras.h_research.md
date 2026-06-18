# sources/distributed-fs/ceph-client/include/linux/ras.h

Purpose: declares Reliability, Availability, and Serviceability hooks for debugfs consumers, corrected-error collection, CPER event logging, ARM hardware error logging, AMD address translation/row retirement, and MPIDR-to-logical CPU mapping.

Important APIs and types: debugfs helpers include `ras_userspace_consumers()`, `ras_debugfs_init()`, and `ras_add_daemon_trace()`. `parse_cec_param()` is available for corrected-error collection. `log_non_standard_event()` and `log_arm_hw_error()` report CPER-style records when `CONFIG_RAS` is enabled. `struct atl_err` carries AMD translation input (`addr`, `ipid`, `cpu`). AMD ATL hooks register/unregister decoders, retire DRAM rows, and convert UMC MCA addresses. `GET_LOGICAL_INDEX()` maps ARM MPIDR to CPU index where supported.

Control flow: platform error handlers parse machine-check/firmware records, log standard or non-standard CPER sections, optionally notify userspace/debugfs consumers, and use AMD or ARM helpers for address/CPU translation.

State and persistence: this header owns no state. Logged errors may reach trace buffers, debugfs, firmware-first logs, or userspace daemons; hardware row retirement has platform persistence outside this header.

Dependencies and integration points: depends on errno, UUID/GUID, CPER, debugfs, AMD ATL, ARM SMP platform headers, and RAS configs. It integrates EDAC/MCE/APEI-style reporting with architecture/platform decoders.

Risks and test signals: risks include disabled-config no-op surprises, wrong severity/section lengths, MPIDR mapping errors, AMD decoder registration races, and address translation failures. Test config matrices, CPER non-standard and ARM records, corrected-error parameter parsing, AMD UMC address conversion, row retirement paths, and userspace RAS daemon detection.

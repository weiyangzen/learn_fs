# sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_version.h

Purpose: this header centralizes the qedf driver version exposed through module metadata, FC host attributes, and QED slowpath parameters.

Important definitions: it defines `QEDF_VERSION` as `8.42.3.0` and the decomposed major/minor/revision/engineering values as `8`, `42`, `3`, and `0`. `qedf_main.c` uses the string in `MODULE_VERSION`, driver banners, FDMI/host symbolic names, and FC host driver version fields. Probe passes the numeric components into `struct qed_slowpath_params` so firmware/common QED code sees the same driver version.

Control flow and state: there is no control flow or mutable state. The file is included by qedf headers/implementation and compiled into consumers as preprocessor constants.

Dependencies and integration points: the values must stay consistent with packaging/release metadata and with the QED common driver expectations. The header is part of the kernel driver ABI visible through sysfs/modinfo-style surfaces rather than a runtime subsystem.

Risks: stale or mismatched version constants can make diagnostics, support scripts, firmware compatibility checks, and FDMI inventory misleading. Because the string and numeric macros are separate, updates must change all five definitions together.

Test signals: build-time inclusion by `qedf_main.c`, `modinfo qedf` reporting the expected version, FC host `driver_version` matching the macro, and probe logs showing matching slowpath version fields.

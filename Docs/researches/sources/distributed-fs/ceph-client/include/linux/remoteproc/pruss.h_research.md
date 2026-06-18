# sources/distributed-fs/ceph-client/include/linux/remoteproc/pruss.h

Purpose: this header exposes TI PRU-ICSS remoteproc consumer helpers for acquiring PRU cores and configuring PRU constant-table entries.

Important APIs/types/functions: it defines `PRU_RPROC_DRVNAME`, `enum pruss_pru_id` (`PRUSS_PRU0`, `PRUSS_PRU1`, `PRUSS_NUM_PRUS`), `enum pru_ctable_idx` (`PRU_C24` through `PRU_C31`), and conditionally available APIs `pru_rproc_get()`, `pru_rproc_put()`, and `pru_rproc_set_ctable()`. `is_pru_rproc()` checks a device's driver string against `PRU_RPROC_DRVNAME`. When `CONFIG_PRU_REMOTEPROC` is disabled, stubs return `-EOPNOTSUPP` or no-op.

Control flow: PRUSS clients request a PRU by device-tree node and index, receive the PRU ID, configure constant table windows if needed, use normal remoteproc operations, and then release with `pru_rproc_put()`.

State and persistence: no state is stored in the header. PRU remoteproc ownership, firmware, and constant-table state live in the PRU remoteproc driver and hardware.

Dependencies and integration points: depends on `linux/device.h`, `linux/types.h`, OF nodes, remoteproc core, and TI PRUSS platform drivers.

Risks: `is_pru_rproc()` relies on driver-string comparison and must stay aligned with the real driver name. Constant table changes are hardware-visible and can break PRU firmware address assumptions. Test signals include disabled-config stub builds, DT PRU acquisition/release, ctable programming readback, and firmware that exercises configured constant entries.

## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-error.c

Purpose: this file implements AFU port error reporting and interrupt ioctls for the DFL port error subfeature.

Important APIs and functions: `__afu_port_err_mask()` writes the port error mask register. `afu_port_err_clear()` performs the required clear sequence: reject AP6 power state, disable the port, mask errors, verify the user-supplied error value matches current errors, clear `PORT_ERROR` and `PORT_FIRST_ERROR`, unmask errors, and re-enable the port. Sysfs attributes under `errors/` expose `errors`, `first_error`, and `first_malformed_req`. `port_err_ioctl()` handles error IRQ number and trigger setup ioctls.

Control flow: feature init unmasks port errors, and uninit masks them. The `errors` sysfs store is the destructive clear operation and must receive the exact current error value. Visibility is conditional on the `PORT_FEATURE_ID_ERROR` feature being enumerated.

State and persistence: error state is hardware register state. The driver masks errors on feature teardown to avoid stale interrupt delivery. Clear operations temporarily alter port reset state and error masks under `fdata->lock`.

Dependencies and integration: it depends on AFU reset helpers from `dfl-afu-main.c`, DFL feature lookup, DFL IRQ helper ioctls, and the port header power-state register. It is included in the AFU compound object and referenced by `dfl-afu.h`.

Risks: clearing errors resets the port, so userspace can disrupt AFU work if it clears during active operations. The exact-match clear ABI can race with newly arriving errors and return `-EINVAL`. If re-enable fails after masking/clearing, the return prioritizes enable failure and the port may remain disabled. AP6 prevents clearing, leaving errors until power state changes.

Test signals: verify sysfs visibility only when the error feature exists, exact-match clear success and mismatch failure, AP6 rejection, disable/enable timeout handling, IRQ ioctl dispatch, and masking behavior on init/uninit.

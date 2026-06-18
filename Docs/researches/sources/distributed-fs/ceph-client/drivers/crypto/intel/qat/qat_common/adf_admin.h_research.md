# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_admin.h

## Purpose
This header declares the QAT admin-message API used by common lifecycle, PM, heartbeat, telemetry, rate limiting, compression diagnostics, and anti-rollback code.

## Important APIs, Types, And Functions
It forward-declares `struct adf_accel_dev` and includes firmware admin message definitions. Declared functions include admin comms init/exit, firmware init, AE counters, PM init/info, timer sync, heartbeat timer, RL init/add/update/delete, firmware timestamp, CNV stats, TL start/stop, and anti-rollback SVN query/commit.

## Control Flow
No executable control flow exists. The declarations define which subsystems can synchronously send admin commands after `accel_dev->admin` is initialized.

## State And Persistence Behavior
No state is declared here beyond the opaque device pointer. Runtime state is maintained by `adf_admin.c`.

## Dependencies And Integration Points
It integrates with `icp_qat_fw_init_admin.h` and every caller that needs firmware control or status data. It is part of the `CRYPTO_QAT` common internal interface.

## Risks
Changing prototypes has broad impact. Admin functions generally assume the device is initialized and firmware/admin AE masks are valid; callers must sequence them correctly.

## Test Signals
Build coverage across admin callers plus runtime exercise of init, PM, heartbeat, telemetry, rate limiting, CNV, and anti-rollback commands validate this header.

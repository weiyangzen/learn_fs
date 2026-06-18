# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_settings.h

## Purpose
`qla_settings.h` is a small settings/version header for the qla2xxx driver. It provides driver-wide timeout/retry constants used by OS integration and includes `qla_version.h` so version definitions are available to code that consumes this settings layer.

## Important APIs, Types, and Functions
The file defines `MAX_RETRIES_OF_ISP_ABORT` as `5`, which bounds adapter online/reset retry logic, and `MAX_LOOP_TIMEOUT` as `60 * 5`, a five-minute loop-ready timeout. It has no functions or types. Its only include is `qla_version.h`.

## Control Flow
The header has no runtime control flow. It participates through preprocessing: constants are compiled into code such as `qla2x00_wait_for_hba_online()` and `qla2x00_wait_for_chip_reset()` in `qla_os.c`, where the timeout value limits waits for DPC/reset activity to settle and for the adapter to become online or chip reset to complete.

## State and Persistence Behavior
There is no mutable state. The constants are compile-time policy, so changing them changes driver behavior for every build that includes this header. The `qla_version.h` include propagates version metadata into the driver build.

## Dependencies and Integration Points
The direct dependency is `qla_version.h`. The important integration point is with qla2xxx initialization, reset, and loop-recovery code that uses the retry and timeout constants to decide when an adapter is considered failed or still recoverable.

## Risks
Increasing the timeout can make unload, error handling, or reset recovery wait much longer in fault scenarios. Decreasing it can produce false failures during slow fabric recovery, firmware reset, or PCI recovery. Because the constants are not runtime-tunable here, any change requires a rebuild and affects all supported qla2xxx hardware families.

## Test Signals
Relevant signals are adapter probe and link-up timing, ISP abort retry behavior, SCSI EH reset latency, loop-down/loop-ready recovery, module unload during recovery, and failure logs from `qla2x00_wait_for_hba_online()` or `qla2x00_wait_for_chip_reset()` when the timeout boundary is reached.

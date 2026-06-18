# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuerror.h

## Purpose
Collects Wave5 firmware/system, command queue, decoder syntax/spec, warning, encoder warning, and debug reason bit values used to interpret firmware fail and warning registers.

## Important APIs, Types, and Functions
Defines common system errors such as `WAVE5_SYSERR_QUEUEING_FAIL`, `WAVE5_SYSERR_VPU_STILL_RUNNING`, watchdog/VCPU timeout, and fatal hangup masks. It enumerates HEVC and AVC SPS/PPS/slice/spec/etc error codes plus warning masks. It also defines `WAVE5_ETCWARN_FORCED_SPLIT_BY_CU8X8` and debug reason codes.

## Control Flow
No executable flow. Callers compare firmware fail reasons against these macros to decide whether to retry, drain, return `-EINVAL`, or time out.

## State and Persistence
No state. Values are transient interpretations of firmware result registers and output info fields.

## Dependencies and Integration Points
Included by `wave5-vpuapi.h`, which is used across frontend/API/backend code. Encoder and decoder completion paths surface these values in debug or warning logs.

## Risks
Mislabeling constants leads to wrong retry/error handling. The fatal mask overlaps broad high bits and should be used with care. Large sets of parser-specific values are hard to test without targeted bitstreams.

## Test Signals
Firmware error injection, malformed HEVC/AVC decode streams, queue-full/queueing-fail encode scenarios, close while VPU is still running, and log verification that fail reasons are surfaced accurately.

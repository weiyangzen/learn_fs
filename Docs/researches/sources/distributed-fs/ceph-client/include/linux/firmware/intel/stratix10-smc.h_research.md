# sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-smc.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-smc.h` defines Intel/Altera Stratix 10 secure monitor call IDs, call encodings, register protocols, and status codes for communicating from EL1 service drivers to EL3 secure firmware. The source was read as a complete 734-line file for this report.

## Important APIs, Types, and Functions

Important macros include `INTEL_SIP_SMC_STD_CALL_VAL`, `INTEL_SIP_SMC_FAST_CALL_VAL`, `INTEL_SIP_SMC_ASYNC_VAL`, status codes, FPGA configuration calls, protected register read/write/update calls, RSU status/update/notify/retry/DCMF calls, ECC DBE notification, service-completed polling, firmware/SVC version calls, mailbox send command, FPGA Crypto Service calls, HWMON temperature/voltage calls, and async poll/RSU async call IDs.

## Control Flow

Service-layer clients choose a FAST call for atomic/synchronous requests or STD/async calls for preemptible longer operations. The caller passes function ID in `a0` and request arguments in `a1` onward, often physical addresses rather than virtual pointers. Some async operations return busy/accepted and require `INTEL_SIP_SMC_SERVICE_COMPLETED` or async poll to retrieve completion data.

## State and Persistence Behavior

The header owns no state. State lives in secure firmware, reserved physical buffers, FPGA configuration state, RSU boot metadata, mailbox transaction IDs, FCS output buffers, and HWMON readings.

## Dependencies and Integration Points

It depends on ARM SMCCC encoding and bit operations. It integrates with Stratix10 service layer, FPGA manager, RSU driver, mailbox command transport, FCS/security services, HWMON, and out-of-tree secure firmware ABI.

## Risks and Edge Cases

The header is shared with secure firmware and is ABI-critical. Physical address arguments must point to DMA-safe/shared buffers. Async/busy status handling must not reuse buffers early. A malformed function ID or wrong FAST/STD mode can fail across firmware versions.

## Test Signals

SMC ABI compile-time value tests, service-layer mocked SMCCC tests, FPGA reconfiguration success/busy/error tests, RSU status/update tests, FCS buffer tests, HWMON read tests, and firmware-version compatibility tests.

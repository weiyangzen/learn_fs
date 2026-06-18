# sources/distributed-fs/ceph-client/drivers/soc/qcom/smd-rpm.c

## Purpose

`smd-rpm.c` implements the legacy Qualcomm SMD-backed RPM request transport. It sends resource vote messages over an rpmsg endpoint, waits for RPM acknowledgments, and populates RPM child devices.

## Important APIs, Types, and Functions

The exported API is `qcom_rpm_smd_write()`. Runtime state is `struct qcom_smd_rpm`, holding the rpmsg endpoint, device, completion, mutex, and last ACK status. Wire structs are `qcom_rpm_header`, `qcom_rpm_request`, and `qcom_rpm_message`. `qcom_smd_rpm_callback()` parses RPM response stacks and completes pending writes. Probe/remove manage endpoint state and child population.

## Control Flow

Probe allocates state, initializes mutex/completion, stores the rpmsg endpoint, and populates children. `qcom_rpm_smd_write()` builds a request packet under a mutex, assigns a monotonically increasing message id, sends via `rpmsg_send()`, and waits up to five seconds for callback completion. The callback validates service type and length, walks stacked messages, translates `err` messages to `-ENXIO` for "resource does not exist" or `-EINVAL`, stores status, and completes the waiter.

## State and Persistence Behavior

The driver keeps volatile endpoint state and a global static message id. RPM firmware applies resource votes persistently according to active/sleep flags until overwritten or reset. There is no local cache of votes in this file.

## Dependencies and Integration Points

It depends on rpmsg/SMD, OF child population, platform children, completion/mutex primitives, and public `<linux/soc/qcom/smd-rpm.h>`. It supports generic `qcom,smd-rpm`/`qcom,glink-smd-rpm` plus older compatibles for existing DTs.

## Risks and Edge Cases

The single completion and mutex serialize all writes, but the completion is not reinitialized before every send; correctness depends on completion state after previous waits. The static message id is not protected outside the mutex and can wrap. Callback does not match ACK message id to the pending request. Response parsing trusts lengths enough to advance through the buffer; malformed firmware messages can skip oddly. `memcpy_fromio()` is used on rpmsg buffer memory.

## Test Signals

Test packet size limit, rpmsg send failure, timeout, ACK success, RPM error text mapping, malformed short responses, stacked response parsing, message id wrap, child population, and multiple resource clients issuing serialized writes.

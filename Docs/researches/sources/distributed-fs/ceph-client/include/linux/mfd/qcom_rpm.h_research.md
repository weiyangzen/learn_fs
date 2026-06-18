# sources/distributed-fs/ceph-client/include/linux/mfd/qcom_rpm.h

## Purpose
`qcom_rpm.h` is a small public interface for Qualcomm RPM MFD users. It hides the concrete RPM controller behind `struct qcom_rpm` and exposes the write operation used by RPM resource clients.

## Important APIs, Types, And Constants
The file forward-declares `struct qcom_rpm`, defines `QCOM_RPM_ACTIVE_STATE` and `QCOM_RPM_SLEEP_STATE`, and declares `qcom_rpm_write(struct qcom_rpm *rpm, int state, int resource, u32 *buf, size_t count)`. The buffer/count pair represents resource payload words for a target RPM state.

## Control Flow And State
Client drivers obtain or are passed an RPM handle by platform/MFD code, build a resource-specific `u32` payload, choose active or sleep state, and call `qcom_rpm_write()`. Control flow and transport details are implemented outside this header, likely serializing writes to RPM firmware and returning a negative errno on failure.

## State And Persistence Behavior
State lives in RPM firmware/hardware, not in this header. Writes can affect active-state behavior immediately or sleep-state behavior that persists until the next low-power transition or subsequent update. The header does not define caching, locking, or ownership rules.

## Dependencies And Integration Points
The only direct dependency is `linux/types.h`. Integration points are Qualcomm regulators, clocks, bus scaling, power domains, or other RPM resource consumers that share the opaque RPM controller.

## Risks
`state` and `resource` are plain integers, so call sites can accidentally pass invalid IDs without type safety. The payload is a mutable `u32 *` rather than `const u32 *`, so implementers and callers must agree whether the buffer may be modified. Count units are words, not bytes; confusing the two would corrupt messages.

## Test Signals
Build coverage should include every RPM client using this declaration. Unit or integration tests should validate active versus sleep writes, invalid resource handling, payload length checking, and error propagation from the RPM transport.

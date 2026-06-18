# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSDevControl.cpp

Purpose: top-level `IRP_MJ_DEVICE_CONTROL` dispatch entry. It routes control-device IOCTLs to kernel control handling and redirector-device IOCTLs to redirector handling.

Important APIs/types/functions: `AFSDevControl()` extracts the current stack location, calls `AFSProcessControlRequest()` for `AFSDeviceObject`, otherwise calls `AFSRDRDeviceControl()`.

Control flow: the device object determines the target namespace. Exceptions are trapped by `AFSExceptionFilter()` with trace dumping.

State/persistence: no local state mutation beyond whatever the delegated IOCTL handler does. Control-device IOCTLs may initialize pools, services, redirector state, tracing, AuthGroups, and shutdown.

Dependencies/integration: depends on `AFSCommSupport.cpp` for control IOCTL dispatch and the redirector implementation for `AFSRDRDeviceControl()`.

Risks: a wrong device-object comparison can expose control IOCTLs to redirector handles or vice versa. The local `pIrpSp` is currently unused after assignment, so future edits should avoid assuming validation happened here.

Test signals: issue representative IOCTLs against control and redirector device objects, verify unsupported/misrouted requests are rejected in delegated layers, and exercise exception tracing.

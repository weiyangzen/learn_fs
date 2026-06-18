# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_tzmem.h

## Purpose
This private header exposes only the TZMem enable hook needed by the SCM core.

## Important API
- `int qcom_tzmem_enable(struct device *dev);`

## Control Flow And Integration
`qcom_scm_probe()` calls `qcom_tzmem_enable()` before creating SCM's TZMem pool. The public allocation APIs live in `linux/firmware/qcom/qcom_tzmem.h`; this private header is for SCM/TZMem internal coordination.

## State And Persistence
No state is stored in the header. The call initializes the singleton device pointer and mode-specific allocator behavior in `qcom_tzmem.c`.

## Risks
The narrow header helps prevent arbitrary users from enabling the allocator. Calling enable more than once fails because the implementation is singleton.

## Test Signals
SCM probe failure with "Failed to enable the TrustZone memory allocator" points to this initialization path. Successful later TZMem pool creation confirms the hook worked.

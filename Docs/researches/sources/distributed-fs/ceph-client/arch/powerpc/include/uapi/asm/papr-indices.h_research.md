<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-indices.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-indices.h

Purpose: Defines PAPR sensor/indicator index and dynamic state ioctl blocks.

Important APIs/types/functions: `LOC_CODE_SIZE`, `RTAS_GET_INDICES_BUF_SIZE`, `struct papr_indices_io_block`, `PAPR_INDICES_IOC_GET`, `PAPR_DYNAMIC_SENSOR_IOC_GET`, and `PAPR_DYNAMIC_INDICATOR_IOC_SET`.

Control flow: Userspace requests index handles or gets/sets dynamic sensor/indicator state by passing either type selectors or token/state/location-code parameters.

State and persistence: Driver and firmware own sensor/indicator state; the union is the serialized ioctl work block.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID, RTAS/PAPR firmware interfaces, and `SZ_4K` sizing from Linux types context.

Risks: Union interpretation depends on ioctl command. Location codes must fit 79 chars plus NUL. Buffer-size assumptions tie to RTAS response limits.

Test signals: PAPR indices userspace ioctl tests, sensor get/set on pSeries, invalid token/location tests, and ABI size checks.

Source read size: 41 lines, 1294 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-indices.h -->

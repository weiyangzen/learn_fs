## sources/distributed-fs/ceph-client/arch/s390/include/asm/sigp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/sigp.h` is a SIGP inter-processor
instruction wrappers in the s390 ceph-client Linux source snapshot. It has 73 lines and 1918 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
order-code constants and inline assembly helpers for issuing SIGP to other CPUs with condition-
code/result handling
Important macros/constants: `__S390_ASM_SIGP_H`, `SIGP_SENSE`, `SIGP_EXTERNAL_CALL`, `SIGP_EMERGENCY_SIGNAL`, `SIGP_START`, `SIGP_STOP`, `SIGP_RESTART`, `SIGP_STOP_AND_STORE_STATUS`, `SIGP_INITIAL_CPU_RESET`, `SIGP_CPU_RESET`, `SIGP_SET_PREFIX`, `SIGP_STORE_STATUS_AT_ADDRESS`, `SIGP_SET_ARCHITECTURE`, `SIGP_COND_EMERGENCY_SIGNAL`, `SIGP_SENSE_RUNNING`, `SIGP_SET_MULTI_THREADING`, `SIGP_STORE_ADDITIONAL_STATUS`, `SIGP_CC_ORDER_CODE_ACCEPTED`, `SIGP_CC_STATUS_STORED`, `SIGP_CC_BUSY`; plus 8 more.
Important types/layouts: `register_pair`.
Important declarations or inline helpers: `volatile`, `CC_TRANSFORM`, `____pcpu_sigp`, `__pcpu_sigp`.

### Control Flow
The header is mostly inline fast-path code: callers enter small assembly sequences, condition-code
extraction converts hardware results into C values, and fallback or wait loops are selected through
architecture facilities and alternative patching.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
SMP startup/stop, CPU reset, emergency signaling, hotplug, and dump paths. Direct include
dependencies detected here: `asm/asm.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for SMP startup/stop, CPU reset, emergency
signaling, hotplug, and dump paths. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
incorrect register pairing or condition-code translation can hang CPU bring-up or emergency stop

### Test Signals
CPU hotplug, IPL CPU calls, panic stop, and SIGP order fault-injection tests

## sources/distributed-fs/ceph-client/arch/mips/ralink/common.h

### Purpose
This header declares shared Ralink SoC information and early platform hooks.

### Important APIs, Types, And Functions
`RAMIPS_SYS_TYPE_LEN` bounds the system type string. `struct ralink_soc_info` records system type, compatible string, memory base/size/min/max, and optional memory-detect callback. It declares global `soc_info`, `ralink_of_remap()`, and SoC-specific `prom_soc_init()`.

### Control Flow
No runtime flow exists in the header. Platform init fills `soc_info` through the selected SoC implementation.

### State, Persistence, And Dependencies
State is external in `soc_info` and SoC files. The struct persists boot-time SoC and memory metadata.

### Integration Points
Common prom/OF code, clock code, and SoC-specific files share this contract.

### Risks
The `compatible` pointer is mutable `unsigned char *` even though callers assign string literals. Memory min/max and detect callback semantics must stay consistent across SoCs.

### Test Signals
Build all Ralink SoC variants and verify `soc_info.sys_type`, compatible string, and memory sizing are populated before OF/device setup.

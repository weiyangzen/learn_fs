# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ldc.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/ldc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/ldc.h` declares the Logical Domain Channel API used by sun4v guest drivers for hypervisor-backed links, queues, shared-memory cookies, and domain variable/reboot/power operations. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 149 lines, 4474 bytes. Primary surface: `struct ldc_channel_config`, `LDC_MODE_*`, `LDC_EVENT_*`, `LDC_STATE_*`, `ldc_alloc/free/bind/unbind/connect/disconnect`, `ldc_read/write`, `ldc_map_sg`, `ldc_map_single`, `ldc_unmap`, `ldc_copy`, dring helpers, and `ldom_*` functions. Symbol scan highlights: `_SPARC64_LDC_H`, `ldom_set_var`, `ldom_reboot`, `ldom_power_off`, `struct ldc_channel_config`, `LDC_MODE_RAW`, `LDC_MODE_UNRELIABLE`, `LDC_MODE_RESERVED`, `LDC_MODE_STREAM`, `LDC_DEBUG_HS`, `LDC_DEBUG_STATE`, `LDC_DEBUG_RX`, `LDC_DEBUG_TX`, `LDC_DEBUG_DATA`, `LDC_EVENT_RESET`, `LDC_EVENT_UP`, `LDC_EVENT_DATA_READY`, `LDC_STATE_INVALID`, `LDC_STATE_INIT`, `LDC_STATE_BOUND`, `LDC_STATE_READY`, `LDC_STATE_CONNECTED`, `LDC_PACKET_SIZE`, `struct ldc_channel`, and 31 more.

### Control Flow
drivers allocate a channel, bind TX/RX queues with the hypervisor, optionally complete an LDC handshake, receive event callbacks for reset/up/data-ready, then send data or map/copy shared memory through transfer cookies. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
opaque `struct ldc_channel` owns queue, state-machine, mapping, and callback state; LDOM variable state is managed by hypervisor/domain services. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/hypervisor.h>`. Integration dependencies: `asm/hypervisor.h`, scatterlists, sun4v LDC hypercalls, vnet/vdisk/vio style drivers, and interrupt delivery.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
reset handling must fully reinitialize driver state; cookie permissions and map/unmap lifetimes are security-critical; queue state races can drop packets.

### Test Signals
LDOM virtual network/disk bring-up, LDC reset/reconnect stress, shared-ring copy/map tests, and event callback ordering tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.

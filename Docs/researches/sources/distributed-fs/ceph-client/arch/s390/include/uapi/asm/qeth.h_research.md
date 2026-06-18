## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/qeth.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/qeth.h` is a qeth network ioctl ABI
in the s390 ceph-client Linux source snapshot. It has 116 lines and 3119 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
ARP cache/query and OAT data structures plus qeth-specific SIOC ioctl numbers
Important macros/constants: `__ASM_S390_QETH_IOCTL_H__`, `SIOC_QETH_ARP_SET_NO_ENTRIES`, `SIOC_QETH_ARP_QUERY_INFO`, `SIOC_QETH_ARP_ADD_ENTRY`, `SIOC_QETH_ARP_REMOVE_ENTRY`, `SIOC_QETH_ARP_FLUSH_CACHE`, `SIOC_QETH_ADP_SET_SNMP_CONTROL`, `SIOC_QETH_GET_CARD_TYPE`, `SIOC_QETH_QUERY_OAT`, `QETH_QARP_MEDIASPECIFIC_BYTES`, `QETH_QARP_MACADDRTYPE_BYTES`, `QETH_QARP_STRIP_ENTRIES`, `QETH_QARP_WITH_IPV6`, `QETH_QARP_REQUEST_MASK`, `QETH_QARP_USER_DATA_SIZE`, `QETH_QARP_MASK_OFFSET`, `QETH_QARP_ENTRIES_OFFSET`.
Important types/layouts: `qeth_arp_cache_entry`, `qeth_arp_entrytype`, `qeth_arp_qi_entry7`, `qeth_arp_qi_entry7_ipv6`, `qeth_arp_qi_entry7_short`, `qeth_arp_qi_entry7_short_ipv6`, `qeth_arp_qi_entry5`, `qeth_arp_qi_entry5_ipv6`, `qeth_arp_qi_entry5_short`, `qeth_arp_qi_entry5_short_ipv6`, `qeth_arp_query_user_data`, `qeth_query_oat_data`, `qeth_arp_ipaddrtype`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
qeth L2/L3 network driver and userspace network management tools. Direct include dependencies
detected here: `linux/types.h`, `linux/ioctl.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for qeth L2/L3 network driver and
userspace network management tools. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
structure drift breaks ARP/OAT diagnostics or adapter-control commands

### Test Signals
qeth ioctl tests, ARP query/add/remove, and OAT readback

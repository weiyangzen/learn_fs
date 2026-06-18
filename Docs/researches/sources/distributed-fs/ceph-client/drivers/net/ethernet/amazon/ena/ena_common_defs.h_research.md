# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_common_defs.h

Purpose: this small ABI header defines the common ENA specification version and the device memory-address representation shared by admin and data-path descriptors.

Important APIs, types, and functions: `ENA_COMMON_SPEC_VERSION_MAJOR` is `2` and `ENA_COMMON_SPEC_VERSION_MINOR` is `0`. `struct ena_common_mem_addr` stores a 48-bit physical address as `mem_addr_low`, `mem_addr_high`, and a reserved 16-bit field that must be zero.

Control flow: there is no runtime control flow. `ena_com.c` fills `struct ena_common_mem_addr` through `ena_com_mem_addr_set()` before sending admin commands with DMA addresses.

State and persistence: the struct appears in transient admin command descriptors and persistent device configuration for queues, host attributes, RSS buffers, PHC output, and control buffers. The header itself has no mutable state.

Dependencies and integration points: it is included by `ena_admin_defs.h` and `ena_com.h`. The ENA communication layer validates addresses against the negotiated DMA width before populating this ABI type.

Risks: ENA operates with 48-bit addresses, so callers must not pass addresses wider than device support. The reserved field must remain zero for firmware compatibility. Changing the version constants affects host-info reporting in `ena_com_allocate_host_info()`.

Test signals: feature setup involving host attributes, queue creation, RSS, customer metrics, PHC, and indirect control buffers validates address encoding. DMA width boundary tests should reject unsupported high addresses before commands reach firmware.

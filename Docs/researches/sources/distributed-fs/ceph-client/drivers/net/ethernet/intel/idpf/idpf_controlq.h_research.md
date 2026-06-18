# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_controlq.h

## Purpose
This private control queue header defines descriptor layout, descriptor flag bits, hardware/MMIO state, default constants, and internal allocation APIs for IDPF control queues. It bridges the public control queue API and the device-specific hardware structure used by the driver.

## Important APIs, Types, And Functions
Key macros are `IDPF_CTLQ_MAX_BUF_LEN`, `IDPF_CTLQ_DESC()`, `IDPF_CTLQ_DESC_UNUSED()`, and `IDPF_CTRL_SQ_CMD_TIMEOUT`. `struct idpf_ctlq_desc` is the hardware descriptor with flags, opcode, length, return value, virtchnl opcode/status, and direct or indirect parameters. Flag macros define DD, completion, error, function type, read, virtchnl, buffer, and host id fields. `struct idpf_hw` stores mailbox and reset MMIO mappings, LAN regions, adapter back pointer, ASQ/ARQ pointers, PCI identity, stopped flag, and the control queue list. Internal APIs declare `idpf_ctlq_alloc_ring_res()` and `idpf_ctlq_dealloc_ring_res()`.

## Control Flow
The descriptor and flag definitions are consumed by `idpf_controlq.c` to fill send descriptors, parse completed descriptors, initialize RX descriptors, and compute unused ring slots. The hardware struct is filled during PCI/device setup and passed into queue init and send/receive paths.

## State And Persistence
`struct idpf_hw` is long-lived adapter hardware state. It persists MMIO mapping information, control queue pointers, PCI ids, and adapter stopped state for the lifetime of the PCI device. Descriptor contents are DMA-visible transient state shared with hardware.

## Dependencies And Integration Points
The header includes `idpf_controlq_api.h` and Linux slab helpers. It depends on `idpf_dma_mem`, list heads, and MMIO resource types. It is included by `idpf.h`, `idpf_controlq.c`, and `idpf_controlq_setup.c`, making it the common contract for queue resource management.

## Risks
Descriptor layout must match hardware exactly; field size, endianness, or flag mistakes break mailbox communication. `IDPF_CTLQ_DESC_UNUSED()` leaves one ring slot empty to distinguish full from empty; changing it can corrupt ring accounting. Host id is a multi-bit field, not a simple flag, and must be masked correctly.

## Test Signals
Build-time structure and endian usage checks are important. Runtime signals include successful mailbox initialization, correct descriptor wraparound, accurate unused count, valid host id routing, and clean handling of DD/ERR/BUF/RD flag combinations.

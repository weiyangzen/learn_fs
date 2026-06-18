# sources/distributed-fs/ceph-client/drivers/net/fddi/defza.h

## Purpose
Defines the register map, ring descriptors, command buffers, status bits, packet request header constants, and private state structure for the DEC FDDIcontroller 700/700-C DEFZA driver. It is the hardware ABI layer used by `defza.c`.

## Important APIs, Types, And Definitions
Register constants describe FZA reset, interrupt event, status, interrupt mask, and control registers under `FZA_REG_BASE`, with bit definitions for reset sequencing, interrupt sources, adapter states, link status, halt reasons, self-test failures, and control actions. `struct fza_regs` overlays the sparse MMIO register layout.

Ring structures include `struct fza_ring_cmd`, `struct fza_ring_uns`, `struct fza_ring_rmc_tx`, `struct fza_ring_hst_rx`, and `struct fza_ring_smt`. Ownership constants define host/FZA/RMC ownership conventions, noting that RMC TX ownership is reversed. Buffer and ring constants define command/unsolicited ring sizes, host RX size, TX buffer addressing, 512-byte TX packet-memory slots, and 4096+512-byte RX buffers.

Command data structures include `struct fza_cmd_init`, `struct fza_cmd_cam`, `struct fza_cmd_param`, `struct fza_cmd_modprom`, `struct fza_cmd_setchar`, `struct fza_cmd_rdcntr`, `struct fza_cmd_status`, and `union fza_cmd_buf`. `struct fza_counters` maps firmware counters. Packet request header constants define PRH bytes for LLC and SMT transmission. `struct fza_private` is the driver-private netdev state. `struct fza_fddihdr` models the on-wire preamble/starting delimiter plus Linux `struct fddihdr`.

## Control Flow Semantics
The header encodes the control protocol followed by `defza.c`: reset moves the adapter through `RESET` and `UNINITIALIZED`; INIT command returns ring locations, default link parameters, revisions, and the link address; MODCAM/MODPROM update receive filtering; PARAM applies link parameters and loopback; TX/RX/SMT rings exchange ownership by setting or clearing `FZA_RING_OWN_MASK`; interrupt event bits wake the corresponding command, RX, TX, SMT, unsolicited, flush, link, or state-change handlers.

## State And Persistence Behavior
The definitions describe volatile MMIO and adapter-memory state. `struct fza_private` persists while the netdev exists and records software shadows for ring indices, interrupt mask, command/state wait flags, reset timer, queue state, stats, and link parameters copied from INIT. RX skb/DMA arrays are populated on open and cleared on close. Firmware rings live in mapped adapter memory and are reinitialized by reset/INIT. No persistent storage is defined.

## Dependencies And Integration Points
The header includes Linux compiler, FDDI, spinlock, timer, and type definitions. It assumes TURBOchannel little-endian behavior in the implementation, but the structures themselves are expressed as native integer fields accessed through MMIO helpers. It integrates with the Linux netdev and DMA APIs through `struct fza_private`, and with FDDI frame definitions through `struct fddihdr` and FDDI frame-control constants used by `defza.c`.

## Risks
Incorrect structure offsets or ring ownership constants can deadlock command, RX, or TX processing. Access-width requirements are implicit in how `defza.c` copies these buffers; future changes must preserve word-aligned packet-memory operations. Ring size macros have compile-time validation for RX size and TX mode, but firmware-returned ring sizes still need sane runtime handling. The command buffer structures mirror a hardware specification and must not be reordered or widened casually.

## Test Signals
Compile coverage should validate the `#error` guards for ring sizing and all users of `struct fza_private`. Runtime validation comes from successful INIT parsing, sensible ring sizes and addresses, correct MAC/revision reads, ownership transitions on all rings, carrier changes, RX/TX/SMT movement, and reset/SHUT state transitions without timeouts.

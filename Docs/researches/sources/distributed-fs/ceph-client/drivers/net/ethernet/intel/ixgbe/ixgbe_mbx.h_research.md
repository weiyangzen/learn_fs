# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_mbx.h

## Purpose
`ixgbe_mbx.h` defines the PF/VF mailbox ABI for ixgbe. It contains mailbox sizes, mailbox register offsets and bit definitions, VF request opcodes, ACK/NACK/CTS flags, PF/VF API revision identifiers, negotiated feature bits, wrapper prototypes, and the mailbox operation table.

## Important APIs, types, and constants
`IXGBE_VFMAILBOX_SIZE` defines the 16-word, 64-byte mailbox payload. `IXGBE_PFMAILBOX_*` flags represent PF/VF ownership, status, ACK, and VF reset control. `IXGBE_MBVFICR_*` masks describe interrupt-cause bits for VF requests and ACKs.

`enum ixgbe_pfvf_api_rev` is the versioned PF/VF mailbox API contract. Existing numeric values must remain stable; new revisions are appended before `ixgbe_mbox_api_unknown`. The command namespace includes reset, MAC, multicast, VLAN, MTU/LPE, MACVLAN, API negotiation, queue discovery, RETA/RSS key reads, xcast mode updates, IPsec SA operations, link-state queries, PF link-state queries, and feature negotiation.

`struct ixgbe_mbx_operations` is the dispatch table used by `hw->mbx.ops`, with raw read/write methods, posted read/write methods, and event checks for message, ACK, and reset. The file declares `mbx_ops_generic` as the shared PF implementation.

## Control flow and integration
The header is the shared contract between mailbox transport code and SR-IOV policy code. `ixgbe_mbx.c` implements the transport and exports wrappers. `ixgbe_sriov.c` interprets `IXGBE_VF_*` opcodes, applies PF policy, and replies with the high-bit message type flags declared here.

## State and persistence
The header defines protocol constants only. Persistent ABI compatibility matters because VF drivers can be older or newer than the PF driver. The API revision enum and opcode values must not be reordered or repurposed.

## Dependencies
It includes Linux integer types and forward-declares `struct ixgbe_hw`. Register macros such as `IXGBE_PFMAILBOX(vf)` and payload offsets are consumed by the transport implementation and by VF command handlers.

## Risks and edge cases
Changing opcode values, API revision ordering, or mailbox word layout can break guest VF drivers. `IXGBE_SUPPORTED_FEATURES` currently advertises IPsec support only; adding feature bits must be matched with command dispatch support and VF compatibility checks. Message flag bits occupy the high nibble, while `IXGBE_VT_MSGINFO_MASK` uses bits 23:16, so new commands must avoid overlapping those fields.

## Test signals
Compatibility tests should load VF drivers using multiple API revisions and verify negotiation, reset, queue discovery, RSS query gating, IPsec feature negotiation, and ACK/NACK semantics. ABI review should confirm all new mailbox commands fit within the 16-word payload and keep existing enum values stable.

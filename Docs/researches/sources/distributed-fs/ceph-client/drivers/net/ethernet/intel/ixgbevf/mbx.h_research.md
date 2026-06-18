# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/mbx.h

## Purpose
`mbx.h` defines the ixgbe PF/VF mailbox register offsets, ownership/status bits, mailbox message result bits, API revision enum, command IDs, response indices, and default polling timing constants.

## Important APIs, Types, and Constants
- Mailbox size and register offsets: `IXGBE_VFMAILBOX_SIZE`, `IXGBE_VFMAILBOX`, `IXGBE_VFMBMEM`, PF mailbox equivalents.
- VF/PF ownership and status bits: `REQ`, `ACK`, `VFU`, `PFU`, `PFSTS`, `PFACK`, `RSTI`, `RSTD`, and read-to-clear mask.
- Message result bits: `IXGBE_VT_MSGTYPE_SUCCESS`, `FAILURE`, `CTS`, and `IXGBE_VT_MSGINFO_*`.
- `enum ixgbe_pfvf_api_rev` captures API versions 1.0 through 1.7 and unknown.
- Command IDs include reset, set MAC/multicast/VLAN/LPE/MACVLAN, API negotiate, queue query, RETA/RSS key, xcast mode, IPsec add/delete, link-state queries, and feature negotiation.

## Control Flow
This header is declarative. Runtime code composes `msgbuf[0]` from command IDs plus result/info bits, then interprets PF replies by masking `CTS` and checking success/failure. API version checks in `vf.c` gate availability of later commands.

## State and Persistence Behavior
No state is stored here, but values define the ABI between VF and PF. The enum notes that existing API numbers must not change and new versions must append at the end, making it a persistent compatibility contract.

## Dependencies and Integration Points
Included by `vf.h` and `mbx.c`; used by `vf.c` and `ixgbevf_main.c` for all PF-mediated operations. The constants must match PF driver and firmware behavior.

## Risks and Edge Cases
- Typo in comment (`exra`) is harmless but confirms this is a low-level ABI header where comments are not enforcement.
- Reordering API enum values would break compatibility.
- Command payload lengths are implicit and must be kept synchronized with users in `vf.c` and PF-side handlers.

## Test Signals
Build coverage should catch missing constants. Behavioral coverage should include API negotiation across all supported revisions, each mailbox command’s success/failure handling, and backward compatibility with older PF drivers.

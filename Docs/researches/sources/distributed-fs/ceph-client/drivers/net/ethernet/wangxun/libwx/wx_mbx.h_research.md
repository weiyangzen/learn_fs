# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_mbx.h

## Purpose
`wx_mbx.h` defines the shared SR-IOV PF/VF mailbox register layout, message flags, mailbox protocol IDs, VF request opcodes, PF notification opcodes, queue-info fields, multicast mode enum, and mailbox helper prototypes.

## Important APIs, types, and functions
Key constants include `WX_VXMAILBOX_SIZE`, PF registers `WX_PXMAILBOX()` and `WX_PXMBMEM()`, VF registers `WX_VXMAILBOX` and `WX_VXMBMEM`, reset cause registers `WX_VFLRE()`/`WX_VFLREC()`, interrupt cause registers `WX_MBVFICR()`, mailbox ownership/status bits, and message type bits `WX_VT_MSGTYPE_ACK`, `NACK`, and `CTS`. `enum wx_pfvf_api_rev` captures supported PF/VF API versioning. `enum wxvf_xcast_modes` captures VF multicast/promiscuous modes. The prototypes expose PF and VF read/write/check helpers plus posted mailbox operations.

## Control flow and behavior
No executable flow exists in this header. The constants define the protocol consumed by `wx_mbx.c` and higher-level SR-IOV message handlers: VFs send opcodes such as reset, set MAC, set multicast, set VLAN, API negotiate, get queues, get RSS RETA/key, update xcast mode, get link state, and get firmware version; PFs answer with ACK/NACK/CTS and notification messages.

## State and persistence
The header owns no state. It defines hardware register addresses and bit assignments that persist in device mailbox registers until read/cleared by PF or VF logic.

## Dependencies and integration points
It relies on Linux bit macros such as `BIT()` and `GENMASK()` and on `struct wx` being visible for prototypes. It is included by mailbox transport and SR-IOV control-plane code.

## Risks and edge cases
Any mismatch between these constants and hardware/firmware protocol breaks PF/VF communication. Message size is fixed to 15 dwords of payload plus a mirrored status word, so new protocol messages must fit or define fragmentation elsewhere. The misspelled `WX_PF_NOFITY_*` names are ABI-internal but can propagate into call sites. API revision values must match VF expectations.

## Test signals
Build tests should catch missing prototypes and constants. Runtime SR-IOV tests should verify each declared VF opcode is encoded/decoded correctly, ACK/NACK/CTS bits are preserved, queue-info fields match PF allocation, and xcast mode requests result in expected receive filtering.

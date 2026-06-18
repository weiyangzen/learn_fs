# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx.h

Purpose: low-level mailbox register layout and transport prototypes for rnpgbe.

Important declarations: defines FW-to-PF and PF-to-FW counter offsets, shared-memory offset, mailbox control/mask access macros, `MUCSE_MBX_REQ`, and `MUCSE_MBX_PFU`. Declares write-wait-ack, init, and poll-read functions.

Control flow: no executable flow; constants drive `rnpgbe_mbx.c`.

State and persistence: no direct state. The constants name hardware bits and offsets whose values persist in device registers during runtime.

Dependencies and integration: includes `rnpgbe.h` for `struct mucse_hw` and mailbox structure.

Risks: PFU/REQ bit definitions are ownership protocol-critical. Incorrect counter offsets would invert request/ack handling.

Test signals: compile coverage plus firmware mailbox command tests that prove PFU acquisition, request notification, and ack detection.

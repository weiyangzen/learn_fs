# sources/distributed-fs/ceph-client/net/nfc/hci/llc_nop.c

Purpose: Implements the pass-through HCI LLC engine named `LLC_NOP_NAME`, used when no additional link-layer framing or connection management is needed.

Important APIs and functions: The local ops are `llc_nop_init`, `llc_nop_deinit`, `llc_nop_start`, `llc_nop_stop`, `llc_nop_rcv_from_drv`, and `llc_nop_xmit_from_hci`; `nfc_llc_nop_register` registers them with the LLC manager.

Control flow: Init records the HCI device, driver transmit callback, HCI receive callback, head/tailroom, and failure callback. Start and stop are no-ops. Receive forwards skbs directly to HCI with `rcv_to_hci`; transmit forwards skbs directly to the driver with `xmit_to_drv`.

State and persistence: A small `struct llc_nop` persists callback pointers and device context for the life of the LLC instance. RX headroom and tailroom are set to zero.

Dependencies and integration points: Used by `llc.c` and selected by name from HCI drivers. It integrates directly with HCI core callbacks and driver xmit callbacks.

Risks: There is no link supervision, retransmission, sequencing, or failure detection; any reliability must be provided by the underlying transport. The stored `llc_failure` callback is unused.

Test signals: Verify that rx and tx skbs are forwarded exactly once, start/stop return success, private state is freed, and HCI allocation receives zero rx head/tailroom for this engine.

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/proto.h

## Purpose
`proto.h` defines the internal protocol vtable and inline wrappers used by the rest of `brcmfmac` to issue data, control, address-mode, TDLS, reorder, interface lifecycle, initialization, and debugfs operations without knowing whether the active bus uses BCDC or MSGBUF.

## Important APIs, types, and functions
- `enum proto_addr_mode` selects indirect or direct firmware address mode.
- `struct brcmf_skb_reorder_data` reserves skb control-buffer space for RX reorder tracking.
- `struct brcmf_proto` is the protocol vtable. It includes handlers for header pull, firmware dcmd query/set, queued/direct TX, address mode, peer deletion/addition, RX reorder, interface add/delete/reset, init completion, debugfs, and private data.
- Inline wrappers include `brcmf_proto_hdrpull()`, `brcmf_proto_query_dcmd()`, `brcmf_proto_set_dcmd()`, `brcmf_proto_tx_queue_data()`, `brcmf_proto_txdata()`, `brcmf_proto_configure_addr_mode()`, `brcmf_proto_delete_peer()`, `brcmf_proto_add_tdls_peer()`, `brcmf_proto_rxreorder()`, interface lifecycle helpers, `brcmf_proto_init_done()`, and `brcmf_proto_debugfs_create()`.

## Control flow
After `brcmf_proto_attach()` installs a concrete vtable, higher-level code calls these inline wrappers. Most wrappers directly dispatch through `drvr->proto`; optional interface lifecycle and init-done hooks check for NULL and no-op when absent. `brcmf_proto_hdrpull()` normalizes a NULL `ifp` output argument to a local temporary pointer so implementations always receive a non-NULL `struct brcmf_if **`.

## State and persistence behavior
`struct brcmf_proto` persists under `drvr->proto`; private implementation state hangs off `pd`. `brcmf_skb_reorder_data` overlays `skb->cb`, so its state is packet-local and lifetime-bound to the skb. No state is persisted outside memory.

## Dependencies and integration points
The header depends on common driver types (`brcmf_pub`, `brcmf_if`), Linux `sk_buff`, Ethernet address length, and protocol implementations that populate the vtable. It is a central integration point between core networking/cfg80211 code and BCDC/MSGBUF transport protocols.

## Risks and edge cases
- Required wrappers assume `drvr->proto` and relevant callbacks are non-NULL; safety relies on `proto.c` validation before use.
- `brcmf_proto_is_reorder_skb()` interprets `skb->cb` as `brcmf_skb_reorder_data`; other skb control-buffer users must not conflict.
- Optional hooks are no-op when missing, so behavior differences between BCDC and MSGBUF can be silent.
- There is a minor style issue in `brcmf_proto_query_dcmd()` spacing (`len,fwerr`) but no behavior impact.

## Test signals
Compile and runtime coverage should exercise all wrappers through both protocol implementations, NULL optional hooks, RX reorder skb markers, dcmd query/set paths, interface add/delete/reset, and debugfs creation. Fault injection should verify no wrapper is called before successful protocol attach.

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/msgbuf.h

Purpose: declares msgbuf protocol constants and public entry points for builds with `CONFIG_BRCMFMAC_PROTO_MSGBUF`.

Important APIs/types: ring depths and item sizes define control, RX post, completion, TX completion, RX completion, and flowring dimensions. `struct msgbuf_buf_addr` is the shared 64-bit DMA address representation split into little-endian low/high words. Public functions attach/detach the msgbuf proto, trigger RX processing from bus interrupts, and request flowring deletion.

Control flow and state: the header switches behavior at compile time. With msgbuf enabled, callers get the real attach/detach/RX/delete functions. Without it, attach/detach become no-op inline stubs so non-msgbuf builds do not need the implementation.

Dependencies and integration: used by bus/protocol setup code and `msgbuf.c`. The constants must match firmware ring ABI and bus-provided ring memory.

Risks: ring item sizes differ for pre-v7 and newer completion formats; any mismatch with bus firmware setup causes completion parsing corruption. Compile-time stubs can hide missing protocol support if callers do not check bus capabilities separately.

Test signals: build both with and without `CONFIG_BRCMFMAC_PROTO_MSGBUF`, validate ring sizes against PCIe firmware capabilities, and exercise RX trigger/delete flowring paths.

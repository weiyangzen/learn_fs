# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/usb.h

Purpose: declares the USB bus public state shared by `usb.c` and the rest of brcmfmac. It is intentionally compact and contains no implementation.

Important APIs and types: `enum brcmf_usb_state` defines the backend lifecycle states: DOWN, DL_FAIL, DL_DONE, UP, and SLEEP. `struct brcmf_stats` counts USB control packet successes and errors. `struct brcmf_usbdev` is the public bus object referenced from `struct brcmf_bus`; it stores back-pointers, current state, queue sizes, MTU, device/chip revision, and control statistics. `struct brcmf_usbreq` is the per-URB request wrapper used in free/post queues and carries a list node, URB, skb, and private bus pointer.

Control flow: this header participates in allocation and queue movement in `usb.c`; callers do not manipulate these fields directly except through the USB bus operations.

State and persistence: all fields are volatile kernel driver state. The only state that survives device reset is what can be rediscovered from USB descriptors and bootloader/chip IDs.

Dependencies and integration: depends on Linux list, URB, skb, and brcmf bus declarations included indirectly by C files. It forms the ABI boundary between brcmf bus core and the USB backend.

Risks and test signals: the key invariant is that `struct brcmf_usbdev_info` embeds `struct brcmf_usbdev` first, as required by `usb.c`. Queue misuse, stale skb pointers, or state transitions not matching `usb.c` expectations show up as URB leaks, flow-control stalls, or invalid bus state logs.

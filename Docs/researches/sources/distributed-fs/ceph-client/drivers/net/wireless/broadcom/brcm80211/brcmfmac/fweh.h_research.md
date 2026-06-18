# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.h

Purpose: Defines firmware event codes, statuses, reasons, wire-format event packets, handler types, vendor event maps, FWEH state, and inline SKB event validation.

Important APIs/types/functions: `BRCMF_FWEH_EVENT_ENUM_DEFLIST`, status/reason/action/role constants, Broadcom OUI/subtype constants, `struct brcm_ethhdr`, `brcmf_event_msg_be`, `brcmf_event`, host-endian `brcmf_event_msg`, `brcmf_if_event`, `brcmf_fweh_event_map`, and `brcmf_fweh_info`.

Control flow: RX paths call `brcmf_fweh_process_skb()` to validate protocol, length, subtype, OUI, and user subtype before queueing through `brcmf_fweh_process_event()`.

State and persistence behavior: Defines runtime handler/event-mask state and transient wire structs copied from SKBs.

Dependencies and integration points: Included by core, cfg80211, vendor, debug, and event code.

Risks: Abstract event codes use bit 31 and require vendor mapping. Packed wire layout must match firmware. Validation assumes the skb mac header points to the Broadcom event frame.

Test signals: Synthetic SKBs with invalid protocol/subtype/OUI/length should drop; valid mapped events should queue and dispatch.

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fweh.c

Purpose: Implements firmware event handling: event-name lookup, handler registration, event mask activation, deferred queue processing, interface-event default behavior, and vendor event-code mapping.

Important APIs/types/functions: `brcmf_fweh_event_name()`, `brcmf_fweh_attach()`, `brcmf_fweh_detach()`, `brcmf_fweh_register()`, `brcmf_fweh_unregister()`, `brcmf_fweh_activate_events()`, `brcmf_fweh_process_event()`, and `brcmf_fweh_p2pdev_setup()`. Internal queue items copy event message and payload for workqueue handling.

Control flow: Attach asks vendor ops to allocate FWEH info, allocates event mask, initializes queue/work. RX validation queues copied events. Worker maps firmware codes, decodes big-endian message fields, handles IF add/change/delete specially, and invokes registered handlers. Activation builds event masks from handlers plus IF and uses vendor or generic activation.

State and persistence behavior: Runtime state includes handler array, event mask, event queue, spinlock, event map, event-code count, and P2P setup flag. Firmware persists enabled event mask.

Dependencies and integration points: Core attaches FWEH and registers watchdog; cfg80211/P2P/vendor modules register handlers. Depends on fwvid, proto, bus, fwil, and interface management.

Risks: Vendor maps must be correct. IF events can race with cfg80211 waits. Detach warns but does not explicitly drain leftover queue items after cancel. Handler failures are logged and ignored.

Test signals: Event mask bits, IF lifecycle, CYW mapped events, malformed event drops, PSM watchdog, and clean detach.

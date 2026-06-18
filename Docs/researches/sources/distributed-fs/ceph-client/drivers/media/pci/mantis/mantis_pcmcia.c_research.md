# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pcmcia.c

- Purpose: Handles CAM PCMCIA physical-layer insertion/removal state and GPIF interrupt mask changes.
- Important APIs/types/functions: `mantis_event_cam_plugin()`, `mantis_event_cam_unplug()`, `mantis_pcmcia_init()`, and `mantis_pcmcia_exit()`.
- Control flow: Init unmasks IRQ0, reads detect status, configures plugin or plugout interrupt mask, sets slot state, and notifies DVB CA. Plugin/unplug handlers debounce by current slot state, pulse card reset values, swap GPIF IRQ masks, and update slot state. Exit clears status and masks IRQ0.
- State and persistence: Maintains `ca->slot_state` and hardware GPIF IRQ mask/status; no persistence.
- Dependencies and integration points: Called by event-manager init/exit and IRQ0 work; integrates with DVB CA EN50221 notifications.
- Risks: The status clear expression combines negated masks in a way that may not clear both bits as intended. Debounce uses fixed delays and assumes only slot 0. Concurrent CAM events depend on serialized work handling.
- Test signals: Test hotplug jitter, initial plugged/empty boot state, repeated insert/remove, and module unload during CAM events.

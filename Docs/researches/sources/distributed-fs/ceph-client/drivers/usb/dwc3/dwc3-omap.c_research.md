# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-omap.c

Purpose: TI OMAP/AM437x DWC3 wrapper driver. It programs wrapper register offsets, UTMI OTG software/hardware mode, extcon-driven VBUS/ID mailbox signals, wrapper IRQ masking/acknowledgement, optional VBUS regulator, and child DWC3 population.

Important APIs, types, and functions: `struct dwc3_omap` stores IRQ, MMIO base, variant offsets, saved UTMI control value, extcon notifiers, and VBUS regulator. `dwc3_omap_set_mailbox()` maps extcon status into UTMI control bits and regulator state. `dwc3_omap_interrupt()` and `_interrupt_thread()` implement masked threaded IRQ handling. `dwc3_omap_map_offset()` handles AM437x offset deltas. `dwc3_omap_set_utmi_mode()` applies DT `utmi-mode`. Probe/remove and sleep callbacks manage lifecycle.

Control flow: probe validates DT, gets IRQ and MMIO, optionally gets `vbus`, enables runtime PM, maps offsets, sets UTMI mode, registers extcon notifiers and seeds initial mailbox state, populates the child DWC3 core, requests a shared threaded IRQ, and enables wrapper IRQ bits. IRQ top half masks interrupts and wakes the thread when misc/core status is present; the thread clears status and re-enables IRQs. Suspend saves UTMI control and disables IRQs; resume restores UTMI and IRQs; complete resynchronizes extcon mailbox state.

State and persistence: persistent software state includes wrapper offset fields, saved `utmi_otg_ctrl`, extcon handles, and regulator pointer. Hardware state lives in UTMI OTG control and IRQ enable/status registers. Extcon notifications update VBUS valid/session/end and IDDIG bits.

Dependencies and integration: uses extcon for cable and host ID state, regulator framework for VBUS sourcing in host mode, platform MMIO/IRQ, OF child population, and runtime/system PM. It integrates with child DWC3 through the standard child node and with wrapper event routing through IRQ0 and IRQMISC registers.

Risks: `dwc3_omap_complete()` assumes `omap->edev` is valid, so sleep paths without extcon need scrutiny. Offset arithmetic differs for AM437x, creating risk of writing wrong registers if compatible is wrong. Regulator enable/disable is driven by ID status and must not conflict with external power. IRQ clear/mask order is central to avoiding storms or lost events.

Test signals: test extcon VBUS/ID transitions, regulator behavior on host attach/detach, AM437x and generic offset paths, IRQ masking/clearing under shared IRQ, suspend/resume restore, and child depopulation on probe failure and remove.

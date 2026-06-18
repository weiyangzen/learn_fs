# sources/distributed-fs/ceph-client/drivers/usb/cdns3/drd.c

Purpose: implements Cadence DRD/OTG register access, controller-version detection, mode programming, OTG interrupt handling, host/device bus request sequencing, VBUS override controls, PHY mode changes, and power-loss detection.

Important APIs/types/functions: exports `cdns_get_id`, `cdns_get_vbus`, `cdns_clear_vbus`, `cdns_set_vbus`, `cdns_is_host`, `cdns_is_device`, `cdns_drd_host_on/off`, `cdns_drd_gadget_on/off`, `cdns_drd_update_mode`, `cdns_drd_init`, `cdns_drd_exit`, and `cdns_power_is_lost`. Key internals are `cdns_set_mode`, `cdns_init_otg_mode`, `cdns_drd_irq`, and `cdns_drd_thread_irq`.

Control flow: `cdns_drd_init` maps OTG registers, detects v0/v1/CDNSP via first register and DID patterns, initializes version-specific register pointers, applies suspend-residency quirks, reads strap mode, registers a threaded OTG IRQ, and verifies readiness. Mode updates call `cdns_set_mode`; OTG mode enables ID/VBUS interrupts. IRQ top-half filters OTG events, clears interrupt vectors, and wakes the thread, which calls `cdns_hw_role_switch`.

State and persistence: persistent state is written into `struct cdns` register pointers, `version`, `dr_mode`, and PHY modes. Hardware state persists in OTG command/status/override/simulate registers until reset or power loss.

Dependencies and integration: integrates with `core.c` role switching, Linux PHY API, MMIO polling helpers, and controller-specific register layouts from `drd.h`.

Risks: readiness waits can timeout; incorrect DID/strap interpretation prevents probe. VBUS override helpers are CDNSP-only no-ops elsewhere. IRQ handling ignores events in low-power mode, so PM wakeup paths must resume before role switching.

Test signals: validate v0/v1/CDNSP probe, strap-limited host/peripheral modes, OTG ID/VBUS transitions, host/device ready-bit timeouts, PHY mode changes, and resume after simulated power loss.

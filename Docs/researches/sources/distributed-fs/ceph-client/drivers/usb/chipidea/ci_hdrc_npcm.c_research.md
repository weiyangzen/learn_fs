# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ci_hdrc_npcm.c

Purpose: implements Nuvoton NPCM USB device-controller glue for ChipIdea, with optional core clock handling and device-mode platform quirks.

Important APIs/types/functions: defines `struct npcm_udc_data`, `npcm_udc_notify_event`, `npcm_udc_probe`, and `npcm_udc_remove`, plus OF matches for `nuvoton,npcm750-udc` and `nuvoton,npcm845-udc`.

Control flow: probe enables the optional clock, fills platform data with aligned-DMA and force-VBUS-active flags, UTMI PHY mode, and reset notification, then creates a `ci_hdrc` child. The reset notification clears all `USBMODE` bits before core mode programming. Remove disables runtime PM, removes the child, and disables the clock.

State and persistence: stores child `ci` platform device, core clock, and platform data. Hardware mode state is reset through the notification path.

Dependencies and integration: integrates with common clock, runtime PM no-callback mode, OF platform matching, and the ChipIdea child-device API.

Risks: `npcm_udc_probe` does not assign `ci->ci = plat_ci` after successful child creation, so remove may dereference an uninitialized child pointer. Device-mode behavior depends on forced VBUS active, which is appropriate for UDC-only designs but not dual-role boards.

Test signals: probe/remove on NPCM hardware, reset notification ordering, aligned DMA transfer tests, and module unload/remove validation to catch the child-pointer issue.

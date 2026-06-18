# sources/distributed-fs/ceph-client/drivers/usb/chipidea/bits.h

Purpose: centralizes ChipIdea register bit masks and field encodings for identification, capability, command/status, port, device link, OTG status/control, USB mode, and endpoint control registers.

Important APIs/types/functions: defines masks such as `DCCPARAMS_DC/HC`, `USBCMD_RS/RST`, `USBi_*`, `PORTSC_*`, `DEVLC_*`, `OTGSC_*`, `USBMODE_CM/DC/SDIS`, endpoint control masks, and PHY type encodings `PTS_UTMI`, `PTS_ULPI`, `PTS_SERIAL`, and `PTS_HSIC`.

Control flow: no executable flow. The macros feed `hw_read`, `hw_write`, OTG IRQ handling, PHY mode configuration, and host/gadget role code.

State and persistence: macros describe persistent hardware bits. Write-one-to-clear fields such as `PORTSC_W1C_BITS` and `OTGSC_INT_STATUS_BITS` are especially stateful at the hardware boundary.

Dependencies and integration: includes EHCI definitions and is shared by core, host, OTG, debug, and glue notify paths.

Risks: several fields are overloaded between LPM and non-LPM register maps; callers must choose `PORTSC` versus `DEVLC` based on `ci->hw_bank.lpm`. Incorrect write-one-to-clear masks can accidentally drop pending events.

Test signals: register-level hardware tests for mode reset, OTG interrupt clear/enable, port test mode, PHY interface selection, and endpoint enable/flush behavior.

# sources/distributed-fs/ceph-client/drivers/usb/misc/ezusb.c

Purpose: Shared helper module for Cypress/Anchor EZ-USB firmware loading, primarily FX1. It exports reset and Intel HEX download helpers for other USB drivers.

Important APIs and types: `struct ezusb_fx_type`, `ezusb_writememory()`, `ezusb_set_reset()`, exported `ezusb_fx1_set_reset()` and `ezusb_fx1_ihex_firmware_download()`. Disabled FX2 variants document possible future support. It depends on `request_ihex_firmware()`, `ihex_next_binrec()`, and `usb_control_msg_send()`.

Control flow: firmware download requests an ihex firmware blob, clears reset, writes records above the internal RAM limit with external-RAM request, asserts reset, writes internal RAM records, then clears reset to run firmware. The split external-first/internal-second order lets the CPU be stopped while internal code is rewritten.

State and persistence: this file keeps no state and exports symbols only; persistence is entirely in target device RAM. Risks include misleading error strings that swap internal/external wording, a misspelled `max_internal_adress` field, no exact transfer-length accounting beyond helper return status, and FX2 support compiled out. Test signals include exported symbol users, missing firmware handling, device reset sequencing, and control-transfer failure propagation.

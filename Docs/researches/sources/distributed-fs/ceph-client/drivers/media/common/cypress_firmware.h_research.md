# sources/distributed-fs/ceph-client/drivers/media/common/cypress_firmware.h

Purpose: public declarations for the Cypress firmware downloader.

Important APIs/types: defines controller type constants `CYPRESS_AN2135`, `CYPRESS_AN2235`, and `CYPRESS_FX2`; declares `struct hexline` with record length, 32-bit address, record type, up to 255 data bytes, and checksum byte; declares `cypress_load_firmware(struct usb_device *, const struct firmware *, int)`.

Control flow: header-only contract; implementation is in `cypress_firmware.c`.

State/persistence: no state. The struct is a temporary parser container for firmware records.

Dependencies/integration: included by USB media drivers that request firmware with Linux firmware APIs and then call the loader for Cypress-based devices.

Risks/test signals: the integer type constants are used as array indices by the implementation, so callers must pass only known values. Compile coverage should ensure USB and firmware types are visible; runtime tests should pair each type with the correct CPU control register through the implementation.

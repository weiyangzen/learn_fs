# Research: sources/distributed-fs/ceph-client/drivers/net/can/usb/peak_usb/pcan_usb_pro.h

Purpose: this header defines the PEAK PCAN-USB Pro and Pro FD vendor request constants, endpoint addresses, command record IDs, record layouts, status bits, LED modes, and shared function prototypes used by `pcan_usb_pro.c` and reused by FD-family code for common vendor control requests and restart completion.

Important APIs, types, and functions: vendor requests are identified by `PCAN_USBPRO_REQ_INFO`, `PCAN_USBPRO_REQ_FCT`, `PCAN_USBPRO_INFO_BL`, `PCAN_USBPRO_INFO_FW`, and `PCAN_USBPRO_FCT_DRVLD`. Endpoint constants describe command and CAN message pipes for Pro-style devices. Firmware and bootloader structures are `struct pcan_usb_pro_blinfo` and `struct pcan_usb_pro_fwinfo`. Command and RX/TX record structures include bit timing, bus activity, silent mode, filter, timestamp enable, device ID, LED, RX message, RX status, RX timestamp, and TX message records. `union pcan_usb_pro_rec` provides a common view for decoder dispatch. Prototypes export `pcan_usb_pro_probe()`, `pcan_usb_pro_send_req()`, and `pcan_usb_pro_restart_complete()`.

Control flow: implementation files use these constants to build bulk command record lists and parse incoming record lists. `pcan_usb_pro.c` uses all classic Pro records directly. `pcan_usb_fd.c` uses the shared endpoint defaults, vendor request helper, driver-loaded function request, firmware info request identifiers, and restart completion callback for FD-family devices.

State and persistence: the header stores no runtime state, but defines layouts for persistent or semi-persistent device state: firmware/bootloader versions, serial number halves, hardware type/revision, channel device IDs, LED mode, timestamp enable mode, bus activity, and filter state.

Dependencies and integration points: it depends on kernel integer/endian types and packed layout semantics. It is included by PEAK protocol implementations and implicitly participates in the shared adapter contract from `pcan_usb_core.h`.

Risks: packed record layout and endianness must match firmware exactly. Record IDs are used as direct indexes into record-size tables, so changes require synchronized updates in implementation files. Endpoint constants double as defaults for devices that do not return extended endpoint metadata. The Pro and FD families share some constants but not all message formats, so callers must not assume every `pcan_usb_pro_*` record applies to FD-family uCAN traffic.

Test signals: build coverage for both classic Pro and FD-family files, firmware info reads through vendor requests, driver-loaded notifications, endpoint validation, channel-ID records, LED records, and decode paths that use `union pcan_usb_pro_rec` sizes.

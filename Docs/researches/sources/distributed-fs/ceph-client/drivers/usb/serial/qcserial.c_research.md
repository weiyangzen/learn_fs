# sources/distributed-fs/ceph-client/drivers/usb/serial/qcserial.c

## Purpose

`qcserial.c` is a Qualcomm WWAN USB serial driver for Gobi QDL/modem devices and selected Sierra Wireless and Huawei layouts. It binds vendor-specific serial functions such as DM/DIAG, AT modem, and NMEA GPS ports while avoiding QMI, NCM, and other network interfaces that belong to network drivers. For actual serial I/O it uses the shared `usb-wwan` implementation.

## Important APIs, Types, and Functions

The driver registers `qcdevice` with the USB serial core. Its ID table assigns layout metadata through `driver_info`: `QCSERIAL_G1K` for Gobi 1000, `QCSERIAL_G2K` for default Gobi 2000+ layout, `QCSERIAL_SWI` for Sierra Wireless, and `QCSERIAL_HWI` for Huawei. `handle_quectel_ec20()` handles the nonstandard five-interface Quectel EC20 layout. `qcprobe()` performs class checks, interface-count and interface-number policy, alternate-setting selection, and whether `usb-wwan` should send setup control. `qc_attach()` allocates `struct usb_wwan_intf_private`, transfers the send-setup flag into `use_send_setup`, and initializes the suspend lock. `qc_release()` frees that private state.

## Control Flow

Probe first rejects non vendor-specific interfaces. For single-interface devices it recognizes QDL download mode, choosing alternate setting 1 on older devices when needed and requiring bulk-in plus bulk-out endpoints. For composite devices it defaults to altsetting 0, then filters by layout. Gobi 1K accepts DM/DIAG on interface 0 with altsetting 1 and modem on interface 2, rejecting serial-dead or QMI interfaces. Gobi 2K+ rejects interface 0 QMI/net and accepts DM/DIAG, modem, and NMEA interfaces. The Quectel EC20 special case accepts interfaces 0 through 3 and rejects NDIS on interface 4. Sierra Wireless accepts interfaces 0, 2, and 3, enabling send-setup for NMEA and modem ports. Huawei rejects known QMI and NCM protocol values and treats remaining vendor-specific functions as serial.

After a successful probe, attach builds the `usb-wwan` private state. Open, close, writes, modem-control ioctls, per-port setup, and suspend/resume are delegated to `usb-wwan`.

## State and Persistence Behavior

State is per matched USB serial interface. During probe, `usb_set_serial_data()` temporarily stores a boolean send-setup decision; attach replaces it with allocated `struct usb_wwan_intf_private`. Release clears serial data and frees the private object. No state survives disconnect or module unload.

## Dependencies and Integration Points

The driver depends on USB, USB serial, TTY, slab allocation, and `usb-wwan`. It integrates with other WWAN drivers by not binding QMI/net, NCM-like, and NDIS interfaces. User space sees the accepted functions as ttyUSB ports for QDL firmware download, diagnostic tools, AT commands, or GPS NMEA control depending on the device layout.

## Risks and Test Signals

The highest risk is layout policy drift. New firmware can change interface counts, numbers, protocols, or altsettings, causing the driver either to reject a valid serial function or claim a network function. Huawei's default-serial rule depends on the exclusion list staying current. Single-interface QDL detection depends on endpoint order and altsetting count. Send-setup must be applied only to interfaces that need it.

Useful tests include QDL one-interface devices with one and two altsettings, Gobi 1K and 2K composite layouts, Quectel EC20 five-interface layout, Sierra Wireless modem and GPS ports with DTR/RTS setup, Huawei protocol filtering against QMI and NCM functions, coexistence with `qmi_wwan` or NCM drivers, attach/release allocation failure paths, and suspend/resume through `usb-wwan`.

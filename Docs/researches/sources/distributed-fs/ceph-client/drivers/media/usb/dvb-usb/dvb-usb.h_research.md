# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb.h

## Purpose
This is the central public header for the legacy DVB USB framework. It defines the common device, adapter, frontend, streaming, remote-control, firmware, and property structures consumed by individual USB DVB drivers in this directory.

## Important APIs, types, and functions
Key types are `dvb_usb_device_properties`, `dvb_usb_adapter_properties`, `dvb_usb_adapter_fe_properties`, `usb_data_stream_properties`, `usb_data_stream`, `dvb_usb_device`, `dvb_usb_adapter`, and `dvb_usb_fe_adapter`. The header exposes `dvb_usb_device_init()`, `dvb_usb_device_exit()`, `dvb_usb_generic_rw()`, `dvb_usb_generic_write()`, `dvb_usb_nec_rc_key_to_event()`, `usb_cypress_load_firmware()`, and `dvb_usb_get_hexline()`. It also defines logging macros, debug helpers, RC5 scancode helpers, adapter capability flags, USB bulk/isoc stream type flags, cold/warm USB ID descriptors, and Cypress firmware controller identifiers.

## Control flow and state
Drivers populate static `dvb_usb_device_properties` tables. The framework consumes those tables at probe time, downloads firmware when needed, allocates `dvb_usb_device` private state, registers I2C adapters and DVB adapters, attaches frontends/tuners, and configures URB streaming. Runtime state is represented by `DVB_USB_STATE_*`, adapter `DVB_USB_ADAP_STATE_*`, stream `USB_STATE_*`, `powered`, feed counts, active frontend, RC delayed work, and mutexes for USB/data/I2C access.

## Dependencies and integration
The header integrates Linux USB, firmware loading, mutexes, rc-core, DVB frontend/demux/net/dmxdev, DVB PLLs, and shared USB ID definitions. Every driver in this work item includes it directly or through a device header and uses its property/callback contract.

## Risks and test signals
Risk centers on callback contract drift, lifetime of `priv` pointers, mutex ordering, and stream property correctness. Useful tests are compile coverage across `CONFIG_DVB_USB`, probe/remove on warm and cold devices, firmware-loading failure paths, I2C transfer stress, RC polling, and stream start/stop with both bulk and isochronous URBs.

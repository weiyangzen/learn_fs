# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dvb-usb-init.c

Purpose: core lifecycle for legacy DVB USB devices. It handles module parameters, matching cold/warm USB IDs, firmware download, device allocation, power sequencing, private allocation, I2C/adapter/frontend/remote initialization, and disconnect teardown.

Important APIs/functions: exported `dvb_usb_device_init()` and `dvb_usb_device_exit()` are called by all legacy device drivers. `dvb_usb_device_power_ctrl()` reference-counts power transitions. Internal `dvb_usb_init()` and `dvb_usb_exit()` perform full setup/teardown. `dvb_usb_adapter_init()` allocates adapter/FE private data, selects PID filtering mode, initializes streams, DVB adapter, and frontends.

Control flow: probe allocates `struct dvb_usb_device`, copies properties, finds a device description in cold/warm ID lists, optionally downloads firmware, stores USB/interface state, and calls `dvb_usb_init()`. Init sets mutexes, allocates device private state, powers on, registers I2C, initializes adapters/frontends/URBs/DVB, starts remote handling, then powers off. Adapter setup forces hardware PID filtering for USB full-speed devices or module option, allocates private buffers, initializes URB streams, registers DVB core objects, and attaches frontends. Disconnect cancels remote work, tears down frontends/DVB/streams/I2C, calls private destroy, frees private memory and device.

State and persistence: persistent device state includes copied properties, matched description, USB device, owner, mutexes, powered reference count, state bits, private memory, initialized adapter count, and per-adapter private/FE private objects. Module parameters include debug, RC polling disable, and forced PID filtering.

Dependencies and integration: central dependency for all drivers in this directory. It integrates with firmware loader, I2C, DVB-core setup, URB streaming, remote-control setup, USB interface data, and property callbacks.

Risks: `dvb_usb_adapter_init()` has failure paths that free `adap->priv` but not all per-FE private allocations in early failures. Power reference counting can underflow if callbacks are imbalanced. Cold firmware devices usually return after download unless `no_reconnect` permits same-probe warm init. Frontend attach returning no FE is treated as nonfatal in some paths.

Test signals: cold/warm probe, firmware failure and success, private init/destroy callbacks, full-speed USB rejection without PID filter, forced PID filter module parameter, multi-adapter init/exit ordering, remote disabled parameter, and repeated bind/unbind under fault injection.

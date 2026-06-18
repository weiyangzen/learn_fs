# sources/distributed-fs/ceph-client/include/linux/i3c/device.h

## Purpose
Defines the I3C device-driver interface, transfer descriptors, device information, ID matching helpers, combined I2C/I3C driver registration, and in-band interrupt management.

## APIs, Control Flow, and State
`enum i3c_error_code` carries M0/M1/M2 protocol error detail. `enum i3c_xfer_mode` distinguishes SDR and HDR modes. `struct i3c_xfer` describes one private transfer with direction/command, length, actual length, DMA-able buffer, and error code. PID/BCR macros decode manufacturer, part, role, HDR, bridge, offline, IBI, and speed-limitation capabilities. `struct i3c_device_info` caches discovered PID/BCR/DCR, static/dynamic address, HDR capability, speed limits, IBI length, turnaround, and max transfer sizes. `struct i3c_driver` wraps device-driver callbacks and ID table. Registration helpers support pure I3C drivers, module boilerplate, and paired I2C/I3C drivers that fall back to I2C-only when `CONFIG_I3C` is disabled. IBI APIs request/free/enable/disable preallocated slots and workqueue-context handlers.

## Dependencies, Integration, Risks, and Tests
Depends on device model, I2C core, module infrastructure, and mod_devicetable IDs. Integrates with I3C master core, dual-mode devices, dynamic address assignment (`i3c_device_do_setdasa()`), private SDR/HDR transfers, and IBI event delivery. Risks include non-DMA-safe buffers, ignoring `actual_len` or `err` after `-EIO`, mismatched I2C/I3C registration rollback, insufficient IBI slots, slow sleeping IBI handlers delaying queued IBIs, and assuming I3C APIs work in !CONFIG builds. Test signals include I3C driver probe/remove, ID matching by PID/DCR/extra info, SDR/HDR transfer vectors, paired I2C/I3C registration failure rollback, IBI flood tests, and disabled-I3C fallback builds.

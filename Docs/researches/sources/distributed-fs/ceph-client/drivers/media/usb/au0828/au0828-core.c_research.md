# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-core.c

## Purpose
Provides AU0828 USB driver registration, register read/write helpers, media-controller source arbitration, probe/disconnect, suspend/resume, and module init/exit.

## Important APIs, types, and functions
`au0828_readreg()` and `au0828_writereg()` wrap vendor control messages. `send_control_msg()` and `recv_control_msg()` perform USB control transfers, with reads serialized by `dev->mutex` and a heap control buffer. `au0828_usb_probe()` validates interface 0 and high-speed USB, allocates state, initializes media/V4L2/I2C/card/DVB/RC layers, and registers media graph support. `au0828_usb_disconnect()` marks `DEV_DISCONNECTED`, unregisters RC/DVB/analog, clears `usbdev`, and releases state. Media-controller helpers register devices, create audio links, enable/disable source links, and handle sharing between analog video/VBI/audio versus DVB.

## Control flow and state
Module init registers the USB driver. Probe creates `struct au0828_dev`, copies board data from `driver_info`, powers up the bridge, configures GPIOs, I2C, card, analog, DVB, and RC. If media controller is enabled, source ownership is tracked with `active_link`, owner/user entities, and pipeline pointers to prevent conflicting tuner use. Suspend/resume calls RC, V4L2, and DVB suspend/resume hooks and re-powers/configures GPIOs.

## Dependencies and integration points
Depends on USB core, V4L2, media controller, DVB, I2C, RC, tuner media entities, and board tables. Exposes `au0828_read()`/`au0828_write()` API used by all AU0828 submodules.

## Risks and test signals
Risks include disconnect races, media graph source ownership bugs, high-speed check override misuse, and asymmetric control-message locking between reads and writes. Test signals include successful probe/unwind on each failure path, correct media graph links, source arbitration returning `-EBUSY` for tuner conflicts, suspend/resume with active streams, and clean disconnect while analog/DVB/RC are open.

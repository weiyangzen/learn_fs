# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb.h

## Purpose
Defines the shared private state, constants, debug helpers, bridge command IDs, Medion analog data structures, and cross-file function prototypes for the CXUSB DVB USB driver. It is the contract between `cxusb.c` and the optional `cxusb-analog.c` implementation.

## Important APIs, Types, And Functions
The header defines USB bridge commands such as `CMD_I2C_WRITE`, `CMD_I2C_READ`, `CMD_POWER_ON`, `CMD_STREAMING_ON`, `CMD_ANALOG`, and `CMD_DIGITAL`, plus GPIO and BT.656 bit masks used by the C files. Video constants include five URBs, a 512 KiB maximum URB transfer, 3030-byte isochronous packets, and frame sizing limits.

Core types:

- `struct cxusb_state`: base private state used by all CXUSB devices, including GPIO cache, optional I2C clients, bounded command buffer, stream mutex, and saved frontend status callback.
- `enum cxusb_open_type`: Medion ownership states for initialization, idle, analog, and digital access.
- `struct cxusb_medion_auxbuf`: rolling byte buffer for analog isochronous payloads.
- `enum cxusb_bt656_mode`, `enum cxusb_bt656_fmode`, and `struct cxusb_bt656_params`: state machine for frame/field and line/VBI parsing.
- `struct cxusb_medion_dev`: Medion-specific private state. It deliberately begins with `struct cxusb_state` so the same `dvbdev->priv` pointer can be used as base CXUSB state or Medion extended state.
- `struct cxusb_medion_vbuffer`: vb2 buffer wrapper with a queue list node.

The public prototypes are `cxusb_ctrl_msg()`, `cxusb_medion_get()`, and `cxusb_medion_put()`. When analog support is enabled, the header also declares `cxusb_medion_analog_init()`, `cxusb_medion_register_analog()`, and `cxusb_medion_unregister_analog()`; otherwise it provides stubs that fail or no-op as appropriate.

## Control Flow
The header has no runtime control flow, but it shapes the driver flow. `cxusb.c` allocates private storage based on property tables and treats `dvbdev->priv` as `struct cxusb_state` for generic devices or `struct cxusb_medion_dev` for Medion. Analog registration and open flows compile to real calls only under `CONFIG_DVB_USB_CXUSB_ANALOG`; without that option, Medion analog initialization fails with `-EINVAL` and registration/unregistration become harmless no-ops.

## State And Persistence
All state described here is transient kernel driver state. `gpio_write_state` and `gpio_write_refresh` cache bridge GPIO state across mode switches. `open_type`/`open_ctr` protect hardware ownership for Medion analog versus digital users. V4L2 state includes subdevice pointers, video/radio devices, current input/norm/format, queued capture buffers, URB completion bits, active parser state, and completion used for release synchronization. No persistent storage or userspace-visible configuration file is defined.

## Dependencies And Integration Points
The header pulls in Linux completion, I2C, list, mutex, USB, workqueue, V4L2, and videobuf2 headers, then includes `dvb-usb.h` under the CXUSB log prefix. It is included by both CXUSB source files and provides their shared debug macro `cxusb_vprintk()`, which assumes the device private pointer is a `struct cxusb_medion_dev` when analog debug output is used.

## Risks
The leading-member layout requirement in `struct cxusb_medion_dev` is important; changing it would break casts in `cxusb.c` that expect `struct cxusb_state` at offset zero. The analog fields are compiled only under a Kconfig guard, so any unguarded access from generic code would break non-analog builds. `MAX_XFER_SIZE` bounds bridge command payloads and must stay in sync with actual command buffer usage. The debug macro is Medion/V4L2-specific and should not be used on generic devices without confirming `priv` layout.

## Test Signals
Build coverage should include both `CONFIG_DVB_USB_CXUSB_ANALOG=y/m` and disabled configurations to exercise real analog prototypes and stub paths. Runtime signals include correct private-size setup for generic versus Medion devices, stable analog/digital open counting, and no compiler warnings when media/V4L2 or DVB USB APIs change.

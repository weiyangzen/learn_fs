# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/go7007-priv.h

Purpose: private cross-module contract for the GO7007 driver. It centralizes board IDs, board capability flags, sensor/audio flag bit layouts, custom motion-detection V4L2 control IDs, core state structures, HPI operations, and inter-file function prototypes.

Important APIs and types: `struct go7007_board_info` describes board capabilities, sensor geometry, audio clocks, I2C devices, video inputs, and audio inputs. `struct go7007_hpi_ops` abstracts transport-specific reset, interrupt, stream, firmware, command, and release methods. `struct go7007_buffer` extends VB2 buffers with frame offset and motion status. `struct go7007` is the primary device object spanning V4L2, ALSA, I2C, parser, streaming queue, HPI, and board state.

Control flow: consumers allocate/fill `struct go7007`, install HPI ops, register I2C/subdevices, initialize V4L2/ALSA, then drive the device using macros such as `go7007_write_addr()`, `go7007_stream_start()`, and `go7007_send_firmware()`.

State and persistence: this header defines all important in-memory state: current input, standard, dimensions, bitrate/GOP, motion maps, active VB2 queue, parser state, interrupt wait queue, audio callback, and adapter identity. No persistent disk state exists.

Dependencies and integration points: depends on V4L2 device/control/filehandle and VB2 headers. It binds together implementation files including driver core, firmware construction, I2C, USB, V4L2, and sound.

Risks and test signals: risks concentrate around shared mutable state protected by different locks (`hw_lock`, `serialize_lock`, `queue_lock`, spinlock), transport ops called through macros without NULL checks, and fixed-size arrays for I2C devices/inputs/motion maps. Test signals include compile coverage across all modules, lockdep during stream/start/stop/disconnect, and bounds checks for board tables and motion region controls.

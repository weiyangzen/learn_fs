# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib0700_core.c

## Purpose
Provides the common USB bridge implementation for DiBcom DiB0700-based DVB USB devices. It handles firmware download and startup, firmware version detection, vendor control reads/writes, legacy and new firmware I2C master protocols, GPIO/clock/I2C-speed configuration, MPEG-TS streaming enable/disable, RC protocol and bulk/interrupt URB handling, USB probe/disconnect, and module registration.

## Important APIs, Types, And Functions
The exported bridge helpers are `dib0700_get_version()`, `dib0700_ctrl_rd()`, `dib0700_set_gpio()`, `dib0700_ctrl_clock()`, `dib0700_set_i2c_speed()`, `dib0700_download_firmware()`, `dib0700_streaming_ctrl()`, `dib0700_change_protocol()`, `dib0700_rc_setup()`, `dib0700_identify_state()`, and `dib0700_i2c_algo`.

Important internal functions include `dib0700_ctrl_wr()` for vendor writes, `dib0700_set_usb_xfer_len()` for firmware 1.20.1+ transfer sizing, `dib0700_i2c_xfer_new()` and `dib0700_i2c_xfer_legacy()` for firmware-specific I2C transactions, `dib0700_set_clock()`, `dib0700_jumpram()` for firmware start, `dib0700_rc_urb_completion()` for RC packet decoding/resubmission, `dib0700_probe()`, and `dib0700_disconnect()`. The module exposes debug and `nb_packet_buffer_size` parameters plus adapter numbering.

## Control Flow
Cold detection in `dib0700_identify_state()` sends `REQUEST_GET_VERSION`; a failed or empty response means cold firmware state. Firmware download parses Intel HEX records using `dvb_usb_get_hexline()`, writes each record over bulk endpoint 1, jumps to RAM address `0x70000000`, sleeps for firmware startup, queries the firmware version, and updates every DiB0700 property table's bulk buffer size based on the requested number of TS packets and firmware constraints.

Probe loops over `dib0700_devices[]` and calls `dvb_usb_device_init()` until a property table claims the interface. It then reads and stores firmware version, copies the TS packet buffer module parameter into private state, selects bulk RC mode for firmware 1.20+, starts RC setup, and returns success. Disconnect unregisters optional tuner/demod I2C clients, drops module references, and exits the DVB USB device.

I2C transfer control branches on `st->fw_use_new_i2c_api`. The new API serializes through `i2c_mutex`, emits individual start/stop flags per message, supports read messages without a preceding write, and uses `REQUEST_NEW_I2C_READ/WRITE`. The legacy API locks both I2C and USB mutexes, supports write-only and write-then-read patterns via `REQUEST_I2C_WRITE/READ`, and returns the number of consumed messages or an error.

Streaming control optionally programs USB transfer length on firmware 1.20.1+, builds `REQUEST_ENABLE_VIDEO`, computes adapter number from endpoint 2/3 or adapter ID fallback, updates `channel_state`, ORs it into the command payload, and sends the vendor write under `usb_mutex`.

RC setup uses firmware version to decide whether bulk/interrupt URB mode is available. `dib0700_rc_setup()` allocates one URB and a six-byte buffer on endpoint 1, accepting either bulk or interrupt IN endpoints. Completion validates packet length, decodes NEC, NECX, NEC32, RC5, and repeat packets depending on selected protocol, reports events through rc-core, clears the buffer, and resubmits the URB.

## State And Persistence
Private state is `struct dib0700_state` from `dib0700.h`. `fw_version`, `fw_use_new_i2c_api`, `nb_packet_buffer_size`, `disable_streaming_master_mode`, and `channel_state` directly influence control paths. The shared `st->buf` command buffer is protected by USB and/or I2C mutexes in most paths. RC state is split between `d->props.rc.core.protocol`, the rc-core device, and the live URB. No data is persisted beyond the running kernel driver, though firmware bytes are loaded from the kernel firmware mechanism.

## Dependencies And Integration Points
This file depends on the DVB USB framework for property tables, firmware parsing, logging, adapter setup, and device exit. It integrates with USB control and bulk APIs, Linux I2C algorithm registration, rc-core scancode helpers, firmware loader declarations via `MODULE_FIRMWARE("dvb-usb-dib0700-1.20.fw")`, and board-specific `dib0700_devices[]`/`dib0700_usb_id_table[]` definitions.

## Risks
`dib0700_get_version()` copies 16 bytes from `st->buf` after `usb_control_msg()` without checking that exactly 16 bytes were returned, so short successful transfers would produce stale/partial version fields. The new I2C read path performs the USB read before checking whether `msg[i].len` fits in `st->buf`; a too-large length asks USB to write past the command buffer, making caller-side I2C length validation important. RC completion resubmits without checking `usb_submit_urb()` return status. Firmware download mutates global device property buffer sizes after firmware version detection, which affects later allocation and should be considered shared module state. Disconnect assumes I2C clients' driver owners are valid when unregistering.

## Test Signals
Useful signals are cold/warm detection for devices with and without firmware, successful firmware load and version print, I2C transfers against demod/tuner chips on both legacy and new firmware, buffer-size behavior when `nb_packet_buffer_size` is varied, TS streaming on/off for endpoint 2 and 3 devices without disrupting the other adapter's `channel_state`, RC key reporting for NEC/RC5/RC6-MCE-capable firmware, and clean disconnect with tuner/demod I2C client cleanup.

# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-blackbird.c

## Purpose
Implements support for Blackbird reference-design MPEG encoder cards that combine a cx2388x bridge with a cx23416 hardware MPEG encoder. It loads cx23416 firmware through the cx2388x host port, sends encoder mailbox commands through the cx2341x API layer, exposes a V4L2 MPEG capture node, and coordinates access to shared cx8802 MPEG hardware with DVB users.

## Important APIs, Types, And Data
The file defines Blackbird/cx23416 command enums, firmware size and register constants, host-port register helpers, a `cx2341x_mbox_func` implementation (`blackbird_mbox_func()`), and a `cx8802_driver` named `cx8802_blackbird_driver`. `blackbird_qops` is the vb2 queue implementation for MPEG buffers. `mpeg_fops`, `mpeg_ioctl_ops`, and `cx8802_mpeg_template` define the V4L2 device surface.

Key functions are `host_setup()`, `memory_write/read()`, `register_write/read()`, `blackbird_api_cmd()`, `blackbird_find_mailbox()`, `blackbird_load_firmware()`, `blackbird_initialize_codec()`, `blackbird_codec_settings()`, `blackbird_start_codec()`, `blackbird_stop_codec()`, vb2 queue callbacks, V4L2 ioctl handlers, `cx8802_blackbird_advise_acquire/release()`, `blackbird_register_video()`, and `cx8802_blackbird_probe/remove()`.

## Control Flow
Module init registers the Blackbird mini-driver with cx8802. Probe rejects boards without `CX88_MPEG_BLACKBIRD`, initializes a `cx2341x_handler`, adds shared video controls, sets up the host port, attempts codec initialization, applies the current TV norm and input mux, initializes a DMA SG vb2 queue, and registers a V4L2 MPEG capture device. Firmware initialization pings the encoder; if ping fails, it resets `MO_SRST_IO`, requests `v4l-cx2341x-enc.fw` via `CX2341X_FIRM_ENC_FILENAME`, verifies exact size and magic, writes firmware dwords over the host memory port, verifies by checksum readback, releases VPU/SPU reset, finds the mailbox signature, and pings/reads version.

Mailbox commands validate a signature word before the mailbox, reject a busy mailbox, mark it busy, write command, timeout, and input words, wait up to one second for firmware completion, read outputs and return code, then clears the flag. Streaming starts by acquiring shared MPEG hardware from cx8802, initializing firmware/codec settings, issuing refresh/initialize/start capture commands, then starting cx8802 DMA from the first active buffer. Stop cancels DMA buffers, sends stop capture, clears cx2341x busy state, releases hardware, and marks queued buffers in error.

V4L2 ioctls constrain format to `V4L2_PIX_FMT_MPEG`, negotiate width/height/field against the current norm, prevent format changes while analog or MPEG queues are busy, forward tuner/frequency/std/input operations to shared cx88 helpers, and restart the codec around frequency changes when already streaming.

## State And Persistence
State is volatile in `struct cx8802_dev`: mailbox address, cx2341x control handler state, MPEG queue, transport packet sizing, current width/height inherited from `cx88_core`, and shared DMA queue. The cx23416 firmware persists only in encoder SDRAM until reset/power loss. Hardware state spans cx88 host-port registers, MPEG transport DMA registers, cx23416 mailbox memory, V4L2 controls, and current tuner/input/std state in `cx88_core`.

## Dependencies And Integration Points
The file depends on the shared cx88 core, cx8802 MPEG DMA helpers, Linux firmware loader, V4L2/vb2 DMA SG, and `media/drv-intf/cx2341x.h`. Board gating is driven by `cx88-cards.c` through `board.mpeg`. Hardware arbitration integrates with cx8802 via `request_acquire`/`request_release`; HVR1300 acquire/release paths switch GPIO ownership between the cx22702 DVB demod and the cx23416 encoder.

## Risks And Test Signals
Risks include firmware absence or wrong image, mailbox corruption or timeouts, host-port read/write timing failures, shared hardware conflicts with DVB, stream stop paths leaving queued buffers or busy controls inconsistent, and only one explicit board-specific acquire path. Test signals are firmware upload success, version logging, `/dev/video*` MPEG node registration, `VIDIOC_STREAMON` producing MPEG packets, clean `VIDIOC_STREAMOFF`, format/frequency changes while idle, expected `-EBUSY` while queues are active, and successful arbitration on HVR1300-class shared boards.

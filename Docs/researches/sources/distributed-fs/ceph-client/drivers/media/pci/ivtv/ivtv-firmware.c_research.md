# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-firmware.c

## Purpose
`ivtv-firmware.c` loads, starts, halts, verifies, and restarts CX23415/CX23416 encoder and decoder firmware. It also initializes the MPEG decoder with a canned MPEG stream and restores selected hardware state after firmware restart.

## Important APIs, Types, and Functions
Key functions are `load_fw_direct()`, `ivtv_halt_firmware()`, `ivtv_firmware_versions()`, `ivtv_firmware_init()`, `ivtv_init_mpeg_decoder()`, `ivtv_firmware_check()`, and internal `ivtv_firmware_copy()`, `ivtv_search_mailbox()`, and `ivtv_firmware_restart()`. The file declares firmware names and required sizes via `MODULE_FIRMWARE()`.

## Control Flow
Firmware init halts existing processors, copies encoder and optional decoder firmware into MMIO memory, releases SPU/VPU reset bits, searches firmware memory for mailbox magic cookies, and pings encoder/decoder firmware. First open retries this path. Decoder initialization sets decoder source parameters, starts playback, asks firmware for a DMA target, loads `v4l-cx2341x-init.mpg`, schedules DMA from host, then stops playback. Health checks ping encoder/audio/decoder paths and, if idle, restart firmware and restore standards, decoder setup, framebuffer, OSD alpha, and output routing.

## State and Persistence
State is firmware image contents in device memory, mailbox pointers in `itv->enc_mbox` and `itv->dec_mbox`, API mailbox cache state, decoder and encoder standards, and OSD/framebuffer restoration hooks. Firmware files are external persistent inputs; loaded state is volatile.

## Dependencies and Integration Points
The file depends on Linux firmware loading, ivtv mailbox/API helpers, cx2341x command IDs, YUV filter checks, ioctl standard setters, OSD helpers, UDMA locking, and `saa7127` output routing.

## Risks and Edge Cases
Firmware size mismatches trigger retries and then fail probe-on-open. Mailbox search relies on magic cookies at 256-byte boundaries. Restart is attempted only when idle; active capture/decoding returns `-EIO`. Decoder audio health uses raw decoder memory counters. Incorrect halt/start ordering can leave firmware dead until reboot on some hardware.

## Test Signals
Validate missing, wrong-size, and correct firmware files; encoder-only CX23416 and encoder/decoder CX23415 paths; mailbox discovery; firmware version logs; decoder init MPEG loading; firmware-dead detection; idle restart with standard/OSD restoration; and active-stream failure behavior.

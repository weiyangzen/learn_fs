# sources/distributed-fs/ceph-client/sound/usb/6fire/chip.c

## Purpose
Owns the TerraTec DMX 6Fire USB driver lifecycle: module parameters, USB probe/disconnect, ALSA card creation, subcomponent initialization, and teardown ordering.

## Important APIs, Types, and Functions
Key routines are `usb6fire_chip_probe()`, `usb6fire_chip_disconnect()`, `usb6fire_chip_abort()`, and `usb6fire_card_free()`. Static module arrays `index`, `id`, `enable`, and `chips` track ALSA card slots. `device_table` matches vendor `0x0ccd`, product `0x0080`. `usb_driver` registers the driver as `snd-usb-6fire`.

## Control Flow
Probe locks `register_mutex`, reuses an existing `sfire_chip` if another interface of the same device is probed, otherwise finds a free card slot. It calls `usb6fire_fw_init()` before card creation; `FW_NOT_READY` means firmware was uploaded and the device should reconnect before ALSA registration. For ready firmware it selects interface 0 altsetting 0, creates an ALSA card, initializes `comm`, `midi`, `pcm`, and `control` in that order, registers the card, stores intfdata, and publishes the chip in `chips[]`. On failure it frees the card, which triggers component destroy callbacks through `private_free`.

Disconnect decrements `intf_count`, removes the chip from `chips[]` on final interface, marks shutdown, disconnects ALSA, aborts live URBs/subsystems, and calls `snd_card_free_when_closed()` last because the embedded chip can be freed immediately.

## State and Persistence
Per-device state is `struct sfire_chip` embedded in ALSA card private data. Slot state persists in `chips[regidx]`, with `intf_count` joining multiple USB interfaces. Runtime component pointers are populated by submodule init and cleared by destroy.

## Dependencies and Integration Points
Integrates with `firmware.c` for cold-start loading, `comm.c` for command/MIDI interrupt transport, `midi.c`, `pcm.c`, `control.c`, ALSA card APIs, and USB core probe/disconnect.

## Risks
Probe holds `register_mutex` across firmware loading and all subsystem initialization, so long firmware/control paths serialize all 6fire registration. Error paths rely on `snd_card_free()` invoking `usb6fire_card_free()` only for initialized pointers. Disconnect must not touch `chip` after `snd_card_free_when_closed()`.

## Test Signals
Test cold firmware upload path returning without card registration, hot ready firmware path, multiple interface probes incrementing/decrementing `intf_count`, failure injection for each component init, and disconnect while PCM/MIDI streams are active.

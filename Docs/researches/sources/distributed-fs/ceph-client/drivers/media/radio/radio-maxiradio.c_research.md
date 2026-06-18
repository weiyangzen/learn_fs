# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-maxiradio.c

Purpose: PCI V4L2 radio driver for the Guillemot Maxi Radio FM2000/Gemtek PCI FM-style card. It delegates tuner behavior to the shared TEA575x interface and implements board-specific PCI I/O pin access.

Important types/APIs: `struct maxiradio` stores `snd_tea575x`, V4L2 device, PCI device pointer, and I/O base. Board callbacks are `maxiradio_tea575x_set_pins`, `get_pins`, and `set_direction`. PCI entry points are `maxiradio_probe/remove`; IDs use vendor `0x5046` and device `0x1001`.

Control flow: probe allocates state, names/registers a V4L2 device, initializes TEA575x private data/ops/card/radio number, reserves PCI I/O region, enables PCI device, stores I/O base, and calls `snd_tea575x_init` to detect/register the tuner radio node. Remove exits TEA575x, powers off the card by writing zero, unregisters V4L2, releases region, and frees state.

State and persistence: TEA575x framework owns most radio state; this driver stores only I/O base and V4L2/PCI objects. Hardware is powered through an output bit and turned off on removal.

Dependencies and integration: PCI core, I/O ports, `RADIO_TEA575X` helper, V4L2 device. Risks include inability to read TEA data (`cannot_read_data = true`), no `pci_set_drvdata()` visible in this file before remove retrieves driver data, and comments note frequency changes may unmute. Test signals include PCI probe/remove, I/O resource conflict handling, TEA575x detection, mono/stereo pin read, and remove power-off.

# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_priv.h

## Purpose
`dst_priv.h` defines the private GPIO-control packet interface between the DST frontend driver and the bt878 bridge. It is the low-level bridge contract used by `dst.c` to enable pins, write output levels, read input levels, and set transport packet size.

## Important APIs, Types, And Functions
The header defines `struct dst_gpio_enable`, `struct dst_gpio_output`, `struct dst_gpio_read`, and `union dst_gpio_packet`. Command IDs are `DST_IG_ENABLE`, `DST_IG_WRITE`, `DST_IG_READ`, and `DST_IG_TS`. It forward declares `struct bt878` and declares `bt878_device_control(struct bt878 *bt, unsigned int cmd, union dst_gpio_packet *mp)`.

## Control Flow
No executable code lives here. `dst_gpio_outb()` in `dst.c` fills `union dst_gpio_packet.enb` for `DST_IG_ENABLE` and `.outp` for `DST_IG_WRITE`; `dst_gpio_inb()` uses `.rd` with `DST_IG_READ`; `dst_packsize()` passes `.psize` with `DST_IG_TS`. The bt878 bridge interprets these commands to manipulate hardware.

## State And Persistence
The packet structs are transient call arguments. Persistent state is in the bt878 bridge and hardware GPIO/TS configuration, not in this header.

## Dependencies And Integration Points
This header bridges `dst.c` and the bt878 implementation. It is intentionally narrower than the public bttv GPIO APIs because DST needs command-style access to bt878-specific GPIO and transport settings.

## Risks
The union relies on the command ID matching the active member; using the wrong member corrupts the bridge request. `dst_gpio_read.value` is `unsigned long` while DST code truncates to `u8`, so bridge-side changes to meaningful high bits would be lost. The header lacks include guards, so repeated inclusion depends on current include patterns not causing redefinition problems.

## Test Signals
Signals include successful DST reset/PIO enable/disable/readiness checks, correct TS188/TS204 packet-size selection, no `bt878_device_control` errors during probe and tuning, and valid GPIO readback during DST handshakes.

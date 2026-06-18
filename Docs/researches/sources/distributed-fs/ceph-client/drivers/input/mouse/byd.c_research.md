# sources/distributed-fs/ceph-client/drivers/input/mouse/byd.c

## Purpose

`byd.c` is a PS/2 psmouse protocol driver for BYD touchpads. It detects the device with a PS/2 command sequence, configures the touchpad into four-byte absolute/relative packet mode with most firmware gestures disabled, converts mixed absolute and relative packets into an absolute pointer position, reports touch/buttons, and uses a timer to synthesize touch release when packets stop.

## Important APIs, Types, and Functions

The exported psmouse hooks are `byd_detect()` and `byd_init()`. `struct byd_data` stores the release timer, psmouse pointer, current absolute coordinates, last-touch time, button states, and touch state. `byd_process_byte()` is the packet handler. `byd_reset_touchpad()` sends the reverse-engineered initialization sequence. `byd_clear_touch()` is the timeout handler. `byd_reconnect()` and `byd_disconnect()` manage reset/retry and cleanup.

## Control Flow

Detection sends four `SETRES` commands with parameter `0x03`, then `GETINFO`, and accepts devices returning `param[1] == 0x03` and `param[2] == 0x64`. Init resets the psmouse, sends the BYD initialization sequence, allocates private state, installs psmouse callbacks, selects packet size 4, disables resync, and converts the input device from relative motion to absolute ABS_X/ABS_Y with button/touch capabilities.

At runtime the packet handler validates the PS/2 always-one bit, waits for four bytes, and switches on byte 3. Absolute packets initialize position at touch start using 8-bit X/Y scaled to the driver’s estimated pad dimensions. Relative packets sign-extend PS/2 dx/dy, integrate velocity over `BYD_DT`, and mark touch active. The handler reports BTN_TOUCH, BTN_TOOL_FINGER, ABS_X/Y, BTN_LEFT, and BTN_RIGHT, then arms a 64 ms release timer. The timer pauses serio RX, clears touch, reports release, and recenters the internal coordinate.

## State and Persistence Behavior

State is per psmouse binding in `struct byd_data`. `abs_x`/`abs_y` persist between packets and are integrated from relative deltas. `last_touch_time` and `touch` decide whether the next absolute packet starts a new movement. The release timer persists until disconnect and is deleted there. Hardware configuration persists in the device until reset/reconnect.

## Dependencies and Integration Points

The driver depends on psmouse core, `libps2` command transport, serio pause helpers for timer-side reporting, Linux input core, and jiffies/timers. `byd.h` declares its psmouse entry points. It is linked into `psmouse.o` by the Makefile when `CONFIG_MOUSE_PS2_BYD` is enabled.

## Risks and Edge Cases

Many BYD command constants are documented but only a subset is used; unsupported gesture packet types are treated as bad data and logged. Absolute coordinates are based on estimated resolution and are not clamped after integrated relative motion, so large deltas may leave nominal bounds before input core clamps or consumers handle them. Touch start uses `time_after(jiffies, last_touch_time + timeout)`, so initial zero state behavior depends on jiffies. `byd_disconnect()` uses `timer_delete()` instead of a synchronous shutdown, making timer concurrency worth reviewing for the target kernel. Reconnect retries detection up to three times with one-second sleeps after reset.

## Test Signals

Tests should cover successful and failed detection signatures, the full initialization command sequence, relative sign extension, absolute packet scaling, release timeout behavior, tap timing around `BYD_TOUCH_TIMEOUT`, button reporting, bad packet first-byte validation, unknown gesture packet rejection, reconnect retry behavior, and disconnect during an active timer.

# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_rtas.c

## Purpose
`hvc_rtas.c` exposes IBM RTAS terminal services as an HVC console. It uses RTAS `put-term-char` and `get-term-char` tokens for basic character I/O on PowerPC systems.

## Important APIs, Types, and Functions
`hvc_rtas_write_console()` writes one byte at a time through `rtas_call(rtascons_put_char_token, ...)`. `hvc_rtas_read_console()` reads characters through `rtascons_get_char_token`. `hvc_rtas_get_put_ops` is the HVC ops table. `hvc_rtas_console_init()` registers the early console and preferred `hvc0`; `hvc_rtas_init()` allocates the runtime HVC device.

## Control Flow
Console init resolves both RTAS tokens, instantiates a fixed cookie vterm at index 0, and adds `hvc0` as preferred console. Device init resolves tokens if needed, verifies the runtime device has not already been allocated, then calls `hvc_alloc()` with a 16-byte output buffer.

## State and Persistence Behavior
Global state consists of the RTAS service tokens and the single `hvc_rtas_dev` pointer. The fixed `hvc_rtas_cookie` distinguishes this console in the HVC core. There is no persistent state outside firmware.

## Dependencies and Integration Points
It depends on RTAS firmware APIs, PowerPC IRQ headers, Linux console initcalls, and the HVC core. It has no IRQ notifier and uses polling.

## Risks and Edge Cases
Missing RTAS tokens cause `-EIO` and no console registration. The read/write loops stop on the first RTAS error and return the partial byte count. Only one runtime device is supported, enforced with `BUG_ON(hvc_rtas_dev)`.

## Test Signals
Signals include RTAS token discovery, early preferred `hvc0`, tty allocation at device init, successful character input/output through RTAS calls, and graceful non-registration when tokens are absent.

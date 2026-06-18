<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hecubafb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/hecubafb.c

Purpose: implements a virtual-memory fbdev driver for Hecuba/Apollo e-ink display hardware, delegating physical I/O to a board-specific `hecuba_board` provider.

Important APIs, types, and functions: fixed display dimensions are 600x800 at 1 bpp. `apollo_send_data()` and `apollo_send_command()` use board callbacks to set data/control lines and wait for ACK transitions. `hecubafb_dpy_update()` sends a full image transfer and display command. Deferred I/O callbacks `hecubafb_dpy_deferred_io()`, `hecubafb_defio_damage_range()`, and `hecubafb_defio_damage_area()` update the display. `FB_GEN_DEFAULT_DEFERRED_SYSMEM_OPS()` and `FB_DEFAULT_DEFERRED_OPS()` provide sysmem fb operations. `hecubafb_probe()` obtains board callbacks from platform data, pins the board module, allocates vmalloc framebuffer memory, initializes deferred I/O, registers fbdev, and calls board init.

Control flow: platform probe requires board platform data, allocates the backing buffer and `fb_info`, wires board callbacks into `hecubafb_par`, enables deferred I/O, registers the framebuffer, then initializes the hardware. Any fb damage or deferred work sends the entire framebuffer to the Apollo controller. Remove cleans deferred I/O, unregisters fbdev, frees memory, calls optional board remove, and drops the board module reference.

State and persistence: framebuffer state is a vmalloc `screen_buffer`; hardware has no partial dirty tracking in this driver. `struct hecubafb_par` stores `fb_info`, board operations, and send helpers. The display is updated from the buffer on deferred/damage events.

Dependencies and integration points: depends on platform data from a board-specific companion driver, `<video/hecubafb.h>` for command constants and board API, fbdev deferred I/O, vmalloc memory, and module reference ownership.

Risks: every damage callback sends a full 600x800/8 byte image, which is expensive for small updates. If `board->init()` fails after `register_framebuffer()`, the error path releases `fb_info` without unregistering or deferred-I/O cleanup in this source. Physical I/O ordering and ACK behavior are entirely trusted to board callbacks.

Test signals: board-data missing path, board module reference failure, vmalloc/framebuffer allocation failure, deferred I/O update sequencing, damage range/area callbacks, command/data ACK ordering with a fake board, `board->init()` failure after registration, and remove with optional board remove callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/hecubafb.c -->

# sources/distributed-fs/ceph-client/drivers/video/vgastate.c

Purpose: shared VGA state save/restore library. It captures and restores VGA register sets, DAC color maps, text memory, and font planes so framebuffer drivers can take over legacy VGA hardware and later return it to the prior console state.

Important APIs, types, and functions: exported `save_vga(struct vgastate *state)` and `restore_vga(struct vgastate *state)`. Internal `struct regstate` stores saved font/text/cmap/register buffers. Helpers include `save_vga_text`, `restore_vga_text`, `save_vga_mode`, `restore_vga_mode`, `save_vga_cmap`, `restore_vga_cmap`, and `vga_cleanup`.

Control flow: `save_vga` allocates `regstate`, optionally saves cmap, mode registers, and fonts/text depending on `state->flags`, defaulting register counts and framebuffer memory base/size when absent. Text/font save temporarily blanks the display and reprograms VGA planes to access font/text planes. `restore_vga` restores mode, fonts/text, then cmap, and always cleans allocated save buffers. Register save/restore handles misc, CRTC, attribute, graphics, and sequencer registers with VGA I/O helper routines.

State and persistence: saved state is heap/vmalloc memory referenced by `state->vidstate` until restore or cleanup. It maps legacy VGA memory with `ioremap` during save/restore. No persistence beyond memory and caller-owned `vgastate`.

Dependencies and integration points: used by legacy fbdev drivers such as `vt8623fb`. Depends on `<video/vga.h>`, fbdev, vmalloc, and direct VGA register/memory access.

Risks: assumes readable/writable VGA DAC and standard VGA plane behavior. Save fails if font memory window is too small or allocations fail. It skips text save when current mode appears graphics. Register programming can disturb active display during save/restore; callers need serialization around hardware ownership. Return convention is `1` for failure rather than negative errno.

Test signals: save/restore around fbdev open/close on VGA-compatible hardware; text console content/font/cmap preservation; 4-plane font paths; memory allocation failure injection; nonstandard `num_*` register counts; depth-4 restore behavior; ioremap failure handling.

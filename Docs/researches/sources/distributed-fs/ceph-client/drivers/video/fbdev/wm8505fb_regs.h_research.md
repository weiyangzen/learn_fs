# sources/distributed-fs/ceph-client/drivers/video/fbdev/wm8505fb_regs.h

Purpose: register offset header for WM8505 GOVR framebuffer hardware. It centralizes offsets used by `wm8505fb.c` for framebuffer base addresses, color space selection, contrast, panning, virtual resolution, timing generator, and DVO/output setup.

Important APIs, types, and functions: no functions or types are defined. Public macros include `WMT_GOVR_COLORSPACE`, `WMT_GOVR_COLORSPACE1`, `WMT_GOVR_CONTRAST`, `WMT_GOVR_BRGHTNESS`, `WMT_GOVR_FBADDR`, `WMT_GOVR_FBADDR1`, `WMT_GOVR_XPAN`, `WMT_GOVR_YPAN`, `WMT_GOVR_XRES`, `WMT_GOVR_XRES_VIRTUAL`, `WMT_GOVR_MIF_ENABLE`, `WMT_GOVR_FHI`, `WMT_GOVR_REG_UPDATE`, `WMT_GOVR_DVO_SET`, `WMT_GOVR_TG`, and timing offsets.

Control flow: not applicable; this file is included by the framebuffer driver and supplies constants for direct `readl`/`writel` register access.

State and persistence: no state. Hardware state is created by consumers writing the defined offsets.

Dependencies and integration points: integrated directly with `wm8505fb.c`; the comments encode partial reverse-engineered meaning of some bits, especially color space and DVO setup.

Risks: offsets and bit meanings are hardware-specific and partially documented. The spelling typo in the framebuffer comment is harmless, but incomplete semantic coverage increases the risk of accidental misuse by future code.

Test signals: compile coverage through `wm8505fb.c`; runtime validation is register behavior during WM8505 probe, mode set, contrast, pan, and blank operations.

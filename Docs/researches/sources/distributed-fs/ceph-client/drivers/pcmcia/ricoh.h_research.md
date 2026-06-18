# sources/distributed-fs/ceph-client/drivers/pcmcia/ricoh.h

Purpose: Defines Ricoh RF5C/RL5C CardBus bridge registers and Yenta override helpers for Ricoh-specific initialization, suspend/resume save/restore, CLKRUN handling, and Zoom Video enablement.

Important APIs and functions: Under `__YENTA_H`, it provides `ricoh_zoom_video()`, `ricoh_set_zv()`, `ricoh_set_clkrun()`, `ricoh_save_state()`, `ricoh_restore_state()`, and `ricoh_override()`. It also defines register offsets and bit masks for mode, power, bridge config, misc control, 16-bit timing, ZV, and CLKRUN.

Control flow: `ricoh_override()` reads and updates 16-bit timing/config registers, enabling prefetch on newer bridges or level timing on older ones, installs the ZV callback for RL5C478, and optionally disables CLKRUN. Save/restore copy five vendor registers into `yenta_socket.private[]`; restore rewrites them and reapplies CLKRUN.

State and persistence: Register snapshots persist in the Yenta socket's private array across suspend. Hardware state persists in PCI config space and ExCA-compatible vendor registers.

Dependencies and integration points: Included directly by `yenta_socket.c` when `CONFIG_YENTA_RICOH` is enabled. It relies on Yenta helper functions `config_read*()` and `config_write*()`, the global `disable_clkrun` module parameter, and PCI vendor/device ids.

Risks: This header contains executable static functions compiled into Yenta, so it is not a passive definition file. CLKRUN disabling is limited to selected revisions and may be necessary for broken cards but can alter power behavior. ZV enablement is narrow and register-specific. Save-state slot allocation must not conflict with other vendor helpers.

Test signals: Ricoh CardBus probe with Yenta, register restore after suspend/resume, CLKRUN messages and stable card operation with `disable_clkrun`, ZV callback behavior on RL5C478, and no regressions on older RL5C46x chips.

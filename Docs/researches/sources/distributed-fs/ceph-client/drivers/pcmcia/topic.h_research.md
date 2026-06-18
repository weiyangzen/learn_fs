# sources/distributed-fs/ceph-client/drivers/pcmcia/topic.h

Purpose: Defines Toshiba ToPIC95/97/100 CardBus bridge registers and Yenta override helpers.

Important APIs and functions: Provides `topic97_zoom_video()`, `topic97_override()`, and `topic95_override()`, plus register/bit definitions for socket, slot, card-control, card-detect, register-control, misc, Zoom Video, audio/video switch, ExCA interface control, and PCI write-buffer config.

Control flow: `topic97_override()` installs a Zoom Video callback. `topic97_zoom_video()` toggles ZV control and audio/video switch bits. `topic95_override()` enables 3.3V support in ExCA interface control, marks Yenta to use ExCA/DF power for 16-bit cards, and disables ToPIC95 CardBus write buffers on older revisions when firmware left them enabled.

State and persistence: Hardware state persists in PCI config and ExCA registers. The Yenta socket flags and `zoom_video` callback persist for the socket lifetime.

Dependencies and integration points: Included by `yenta_socket.c` when `CONFIG_YENTA_TOSHIBA` is set and uses Yenta helper functions and flags.

Risks: ToPIC95 power handling changes Yenta's generic power path for 16-bit cards. Write-buffer disabling is a hardware erratum workaround and revision-gated. ZV register effects are chipset-specific.

Test signals: Probe of Toshiba ToPIC95/97/100 bridges, stable 16-bit 3.3V card power, absence of CardBus lockups under load on affected ToPIC95 systems, and ZV callback toggling on ToPIC97/100.

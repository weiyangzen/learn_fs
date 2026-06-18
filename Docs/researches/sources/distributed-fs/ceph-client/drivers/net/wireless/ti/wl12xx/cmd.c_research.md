# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/cmd.c

Purpose: Implements wl12xx firmware command helpers for INI/NVS general parameters, radio parameters, extended RF compensation, and channel switch commands.

Important APIs and functions: `wl1271_cmd_general_parms()`, `wl128x_cmd_general_parms()`, `wl1271_cmd_radio_parms()`, `wl128x_cmd_radio_parms()`, `wl1271_cmd_ext_radio_parms()`, and `wl12xx_cmd_channel_switch()`.

Control flow: General parameter commands validate NVS presence and FEM index, copy chip-specific NVS general parameters, optionally force FEM auto-detect in PLT mode, override ref/TCXO clocks from platform/private config, send a firmware test command, then copy back the detected FEM manufacturer. Radio parameter commands select the FEM-specific NVS entry and send static/dynamic 2.4/5 GHz radio parameters. Extended radio parameters send per-channel power compensation arrays. Channel switch allocates a command, fills role/channel/count/stop flags from mac80211, and sends `CMD_CHANNEL_SWITCH`.

State and persistence: Reads and mutates the in-memory NVS blob for FEM manufacturer, stores detected FEM in `wl->fem_manuf` during calibrator mode, and uses `priv->conf.rf` compensation and `priv->ref_clock`/`tcxo_clock`. No disk persistence.

Dependencies and integration points: Called by `wl12xx_hw_init()` and channel-switch wlcore op. Depends on wlcore command transport, `conf.h`, `wl12xx.h` NVS layouts, and mac80211 channel switch data.

Risks: FEM index bounds are critical before indexing dynamic radio parameter arrays. The functions return `-ENODEV` without NVS, so NVS loading is mandatory except special flows. Incorrect clock override values can make firmware radio calibration fail.

Test signals: Boot/hw init on wl127x and wl128x with valid NVS, PLT FEM auto-detect, channel switch completion events, and command failure warnings.

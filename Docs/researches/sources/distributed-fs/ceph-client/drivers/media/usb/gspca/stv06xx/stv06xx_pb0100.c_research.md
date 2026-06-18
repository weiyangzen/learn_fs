# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/stv06xx/stv06xx_pb0100.c

Purpose: implements the Photobit PB-0100 sensor backend for STV06xx bridges, including mode windows, start/stop, auto/manual gain and exposure controls, red/blue balance, and autogain target programming.

Important APIs and functions: sensor callbacks are `pb0100_probe`, `pb0100_init`, `pb0100_start`, `pb0100_stop`, `pb0100_init_controls`, and `pb0100_dump`. Control helpers include `pb0100_set_gain`, `pb0100_set_red_balance`, `pb0100_set_blue_balance`, `pb0100_set_exposure`, `pb0100_set_autogain`, and `pb0100_set_autogain_target`.

Control flow: probe reads `PB_IDENT`, checks the high byte for `0x64`, and installs 320x240 cropped or 352x288 modes. Control init allocates `struct pb0100_ctrls`, builds an autogain cluster containing gain/exposure/red/blue/natural-light controls plus a target control, and stores it in `sensor_priv`. Init resets and programs bridge/sensor registers for gain, auto-exposure limits, black level, row timing, and bridge scan registers. Start inspects negotiated endpoint packet size to choose row speed, programs crop/window registers by mode, sets STV bridge X/Y/scan controls, and enables streaming. Stop aborts frame and clears the run bit.

State and persistence: `sensor_priv` holds V4L2 control pointers for the PB0100 cluster. Hardware values are volatile and re-applied on init/start or when controls change.

Dependencies and integration points: depends on STV06xx I2C/bridge helpers, `stv06xx_pb0100.h` register definitions and descriptor, V4L2 auto clusters, and GSPCA current format state for autogain target pixel calculations.

Risks: init explicitly lacks full error handling per comments, so failed writes can be ignored. Control IDs include custom user-class offsets, and the names appear swapped in dispatch: ID `+0x1001` triggers autogain target although the config labels `+0x1000` as target. Private control allocation must be freed by STV06xx cleanup. Subsample mode is flagged but disabled/commented as wrong.

Test signals: PB0100 probe, both modes, low-bandwidth packet-size fallback, autogain/manual cluster transitions, red/blue balance clamping, exposure/gain writes, and unload/reprobe leak checks.

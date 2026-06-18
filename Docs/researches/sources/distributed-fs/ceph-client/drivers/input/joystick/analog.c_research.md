# sources/distributed-fs/ceph-client/drivers/input/joystick/analog.c

Purpose: Generic analog joystick/gamepad gameport driver. It supports classic resistor-capacitor timed axes, cooked gameport mode, several CH Flightstick/FCS/Saitek extensions, two logical devices per port, and module-parameter type overrides.

Important APIs/types/functions: `struct analog_port` tracks gameport, two `struct analog` devices, detected axis mask, cooked/raw mode, calibration, button state, failure counts, and timing calibration. `analog_parse_options()` interprets `map=` strings or numeric masks. `analog_init_port()` tries raw mode first, calibrates timing, detects Saitek behavior, then falls back to cooked mode. `analog_init_masks()` derives device capability masks from detected axes and configured options. `analog_cooked_read()` measures axis discharge times; `analog_button_read()` reads normal/CHF/Saitek buttons; `analog_decode()` reports events.

Control flow: Module init parses options and registers a gameport driver. Connect allocates port state, initializes raw or cooked access, derives masks, installs a 10 ms poll handler, and registers one or two input devices. Polling alternates between full axis reads and cheaper button-only reads where possible, then decodes events for active logical devices.

State and persistence: Per-port state persists until disconnect. Initial axis values become calibration baselines and input ABS ranges. `bads` and `reads` accumulate and are logged at disconnect. Module parameters affect all ports, with FIXME comments noting incomplete per-port option handling.

Dependencies and integration points: Uses gameport raw/cooked modes, `gameport_calibrate()`, input core, `seq_buf` for names, high-resolution timekeeping, and module parameter arrays.

Risks: Timing depends on CPU/gameport behavior and can break under virtualization or heavy interrupt latency. Option parsing partly uses only `analog_options[0]`, so multiple ports may not be independently configurable. Auto-detection can misclassify non-analog devices. Calibration based on first sampled values can produce poor ranges if the stick is not centered.

Test signals: Raw and cooked gameport devices; `map=auto`, named masks, numeric masks, and bad strings; Saitek/CHF/FCS paths; two-device split; disconnect failure-rate logging; ABS min/max/fuzz/flat after centered and off-center probe.

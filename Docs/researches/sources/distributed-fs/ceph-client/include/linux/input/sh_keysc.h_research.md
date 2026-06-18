<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/sh_keysc.h -->
# sources/distributed-fs/ceph-client/include/linux/input/sh_keysc.h

Purpose: Defines platform information for SuperH key scan controller drivers.

Important APIs/types/functions: `SH_KEYSC_MAXKEYS` sets a 64-key map. `struct sh_keysc_info` includes one of six scan modes, scan timing, delay values, KYCR2 delay, and keycodes for the KEYIN x KEYOUT matrix.

Control flow: Driver probe programs scan mode/timing and uses keycodes to translate scan results into input events.

State/persistence: Platform scan/keymap settings persist for the controller lifetime.

Dependencies/integration: Integrates SH platform code and input key events.

Risks: Mode and timing values must match board wiring; bad delay settings can cause missed/ghost keys.

Test signals: Each scan mode, max key map, key press/release matrix events, and timing variation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/sh_keysc.h -->

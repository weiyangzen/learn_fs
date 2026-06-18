# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/dphy.h

Purpose: shared DPHY data structure and control function declarations for the RP1 CSI-2 stack.

Important APIs/types/functions: `struct dphy_data` contains device pointer, MMIO base, selected DPHY rate, maximum lanes, and active lanes. Declares `dphy_probe()`, `dphy_start()`, and `dphy_stop()`.

Control flow: no implementation; CSI-2 code owns call sequencing.

State and persistence: state is embedded in `struct csi2_device` and updated during endpoint parsing and stream start.

Dependencies and integration: includes MMIO and integer types. Used only by `csi2.h`/`csi2.c` and `dphy.c`.

Risks: fields are trusted by `dphy_start()` without defensive clamping; callers must validate lane count and rate.

Test signals: compile coverage and stream tests confirming endpoint lane counts propagate into DPHY programming.

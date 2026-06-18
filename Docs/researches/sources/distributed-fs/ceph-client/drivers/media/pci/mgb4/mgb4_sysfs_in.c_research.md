# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_in.c

- Purpose: Input-video sysfs interface for MGB4 status and deserializer/FPGA configuration.
- Important APIs/types/functions: Common attributes include input id, OLDI lane width, color mapping, link/stream status, resolution, sync status/gaps, pixel clock, porch widths, and frequency range; FPDL3 adds input width; GMSL adds mode, stream id, and FEC.
- Control flow: Show handlers read FPGA registers and deserializer registers. Store handlers parse numeric values, validate ranges, update FPGA bits and/or I2C registers, sometimes reset links. Frequency range and stream ID changes lock the video device and reject busy queues; live-safe changes intentionally skip queue locks.
- State and persistence: State updated includes FPGA config/sync registers, `vindev->freq_range`, and deserializer registers. No disk persistence.
- Dependencies and integration points: Used by `mgb4_vin_create()` via module-specific attribute groups; depends on MGB4 I2C, CMT, video locks, and module-type macros.
- Risks: Live configuration writes can disrupt active signals by design. Some multi-register I2C updates OR errors together and return generic `-EIO`. The code checks FPGA/I2C lane-width consistency and returns errors if they drift.
- Test signals: Test every sysfs attribute per FPDL3/GMSL1/GMSL3, invalid values, busy queue rejection, live link reset behavior, and consistency after replug or firmware reset.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_reg.h

Purpose: defines the HIBMC DP transmitter and SERDES MMIO register map, bit fields, and SERDES tuning constants used by the DP hardware, AUX, training, colorbar, interrupt, and timing paths.

Important APIs/types: register offsets include AUX command/data/status, HPD status, PHYIF control, video timing/MSA/packet/control, colorbar, timing generator, HDCP config, reset/clock/gctl, interrupt status/clear/enable, timing sync, and SERDES lane/rate/status registers. Field macros use `BIT()` and `GENMASK()` so callers can use `FIELD_PREP/FIELD_GET` helpers.

Control flow: the header has no executable control flow, but its constants drive sequencing in `dp_hw.c`, `dp_link.c`, `dp_serdes.c`, and the HIBMC PCI IRQ handler. The SERDES constants form the TX de-emphasis table selected from DP training voltage swing and pre-emphasis requests.

State and persistence: hardware register writes based on these definitions persist in device MMIO until reset or power transition. No in-memory state is defined here.

Dependencies and integration points: used by HIBMC DP source files and by `hibmc_drm_drv.c` to probe DP block presence and read/clear DP interrupt status. It assumes Linux bitfield macro availability through including C files.

Risks: register maps are hardware-contract sensitive. A wrong offset or field mask can silently break AUX, HPD, link training, or timing. The SERDES tuning table is hardcoded to hardware-specific values and requires hardware validation for new silicon.

Test signals: low-level MMIO trace comparison against hardware documentation, successful AUX transactions, HPD interrupts, link training status, colorbar output, and mode timing correctness exercise these definitions.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00479_clk_loss_detector_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00479_clk_loss_detector_memmap_package.h

Purpose: Register map for the FPGA clock-loss detector used to validate incoming video clock presence.

Important APIs/types: `struct m00479_clk_loss_detector_regmap` exposes control, status, reference-clock count, and required test-clock count. Masks define enable and clock-missing status.

Control flow: Capture start programs reference/test counts based on freewheel clock and expected pixelclock, then enables detection. IRQ handling resets the detector when clock is missing and keeps frames unstable until clock returns.

State/persistence: Hardware status indicates current clock presence. Threshold registers persist until changed.

Dependencies/integration: Used by V4L2 start/stop/log-status and IRQ lock recovery via `COBALT_CVI_CLK_LOSS()`.

Risks: Threshold calculation uses integer scaling and a 0.5 percent lower bound; unusual timings or clock tolerances may false-positive clock loss.

Test signals: Clock present/missing log-status, cable disconnect/reconnect, nonstandard pixelclock tolerance, and detector reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00479_clk_loss_detector_memmap_package.h -->

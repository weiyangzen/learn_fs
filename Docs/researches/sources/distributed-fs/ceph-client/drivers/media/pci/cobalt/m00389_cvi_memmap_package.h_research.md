<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00389_cvi_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00389_cvi_memmap_package.h

Purpose: Register map for the Cobalt video input block that gates/locks the incoming video stream and tracks configured frame size.

Important APIs/types: `struct m00389_cvi_regmap` maps control, frame width/height, freewheel period, error color, and status. Bit masks define enable, sync polarity bits, lock status, and error status.

Control flow: Capture startup programs frame width/height and leaves CVI disabled until the IRQ stability state machine sees correct measurement and clock status. The IRQ handler enables CVI and waits for lock before disabling forced freewheel.

State/persistence: Hardware control and status reflect current capture path state. Stream flags mirror portions of the state machine.

Dependencies/integration: Used by V4L2 start/log-status and IRQ lock handling through `COBALT_CVI()`.

Risks: Enabling CVI too early produces unstable frames; missing lock forces recovery. Register layout must match the FPGA.

Test signals: Lock/no-lock transitions, frame size programming, error status logging, and recovery after signal loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00389_cvi_memmap_package.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00473_freewheel_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00473_freewheel_memmap_package.h

Purpose: Register map for the FPGA freewheel block that generates fallback timing/color when input video timing is unstable or missing.

Important APIs/types: `struct m00473_freewheel_regmap` maps control, status, active/total lengths, data width, output color, and measured clock frequency. Masks define enable, forced freewheel mode, and freewheel status.

Control flow: Capture start programs active/total lengths and output color, then enables forced freewheel. IRQ stability handling disables forced mode when CVI locks, enables normal freewheel monitoring, and restarts forced freewheel after lock loss.

State/persistence: Hardware state tracks freewheel mode and clock/timing parameters. Stream flags track the staged transition out of forced freewheel.

Dependencies/integration: Used by V4L2 start/stop/log-status and IRQ stability handling via `COBALT_CVI_FREEWHEEL()`.

Risks: Incorrect active/total length calculations cause bad fallback timing. Freewheel status drives error-frame decisions, so FPGA/software semantic drift can affect capture quality.

Test signals: Forced freewheel on stream start, transition to video passthrough after stable lock, re-entry on signal loss, and log-status status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00473_freewheel_memmap_package.h -->

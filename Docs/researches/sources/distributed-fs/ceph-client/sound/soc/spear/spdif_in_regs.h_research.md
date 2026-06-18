# sources/distributed-fs/ceph-client/sound/soc/spear/spdif_in_regs.h

Purpose: register map and bit definitions for the SPEAr S/PDIF input controller.

Important APIs/types: defines control, IRQ mask/status, and lock-status offsets. Control bits cover parity/status/user/valid/block capture, sample mode, data swap/revert, extraction mode, enable, sample, and FIFO threshold. IRQ bits cover FIFO write error, empty FIFO read, FIFO full, and out-of-range.

Control flow/state: no code; values are consumed by `spdif_in.c` to program and diagnose hardware.

Dependencies/integration: private header for the SPEAr input driver.

Risks/test signals: incorrect bit definitions directly affect hardware programming. Tests should compare against the SoC reference manual and validate IRQ/status behavior on real hardware.

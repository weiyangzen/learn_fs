# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/isys_stream2mmio_global.h

Purpose: defines the public Stream2MMIO configuration structure and declares per-controller SID limits.

Important APIs/types/functions: `stream2mmio_cfg_t` stores `bits_per_pixel` and `enable_blocking`. `N_STREAM2MMIO_SID_PROCS` provides active SID count per controller.

Control flow: no direct flow. Configuration code uses `stream2mmio_cfg_t`; state/dump helpers use SID counts.

State and persistence: config is caller-owned. Hardware state persists only after register writes.

Dependencies and integration: depends on CSS type support and generated Stream2MMIO ID types. It bridges MIPI backend output into MMIO storage paths.

Risks and test signals: blocking behavior can stall input if no command is queued. Tests should validate bits-per-pixel programming, blocking enable, and controller-specific SID limits.

# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_hal.c

Purpose: programs NITROX hardware units after software queues and BAR mappings exist, and extracts hardware identity from fuses/reset registers.

Important APIs and control flow: configuration functions enable EMU SE/AE cores, reset and configure packet input rings and solicit ports, program NPS core PF/VF mode, enable NPS packet/core interrupts, configure AQM rings and interrupt enables, set POM/BMI/BMO thresholds, enable RNG, enable EFL and LBC interrupts, invalidate LBC, and toggle PF-to-VF mailbox interrupts. `nitrox_get_hwinfo()` computes frequency, enabled core counts, ZIP availability, and part name.

State and persistence: writes persistent hardware registers for rings, queues, interrupts, core enables, LBC cache state, RNG, and SR-IOV mode. It reads fuse/reset state into `ndev->hw`.

Dependencies and integration points: depends on `nitrox_csr.h`, `nitrox_dev.h`, queue DMA addresses from `nitrox_lib.c`, ISR recovery helpers, and SR-IOV code for mode/mailbox changes.

Risks and test signals: risks include bounded polling that does not report timeout failure, enabling all fused-off cores before relying on fuse counts, all-ones interrupt masks, and queue reconfiguration without external quiesce guarantees. Test signals include rings becoming enabled, doorbell/count registers reset, interrupts firing on completions/errors, LBC invalidation done bit, RNG enabled, and debugfs part name/frequency matching hardware.

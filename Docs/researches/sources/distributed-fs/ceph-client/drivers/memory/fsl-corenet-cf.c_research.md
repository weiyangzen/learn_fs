# sources/distributed-fs/ceph-client/drivers/memory/fsl-corenet-cf.c

## Purpose
`fsl-corenet-cf.c` reports Freescale/NXP CoreNet Coherency Fabric errors. It enables fabric error interrupts, decodes captured address/source metadata, and logs critical diagnostics.

## Important APIs, Types, And Functions
`enum ccf_version` distinguishes CCF1 and CCF2 hardware. `struct ccf_info` stores version, error-register offset, and whether the BRR register exists. `struct ccf_err_regs` maps the error register block, and `struct ccf_private` stores match info, device, MMIO base, error-register pointer, and T1040 detection.

`ccf_irq()` reads big-endian error-detect, capture attribute, address, and secondary attribute registers, rate-limits logging, decodes LAE/CV/UTID/MCST and source id, clears errors by writing `errdet`, and returns IRQ status. `ccf_probe()` maps registers, selects match data, detects T1040 through `CCF_BRR`, requests the IRQ, and enables appropriate error bits. `ccf_remove()` disables CCF1 or CCF2 interrupts.

## Control Flow
Probe maps the controller, computes the error-register base from the selected hardware version, installs an IRQ, then enables LAE/CV and optional T1040-specific errors. Interrupt handling reads and logs details only when the rate limiter allows, but it always writes `errdet` back to clear captured events.

## State And Persistence
Driver state is `struct ccf_private`; persistent hardware state is interrupt-enable and error-capture registers. There is no suspend/resume support and no sysfs/debugfs surface.

## Dependencies And Integration Points
It integrates with OF compatibles `fsl,corenet1-cf` and `fsl,corenet2-cf`, platform IRQs, big-endian MMIO accessors, Linux ratelimit state, and platform-driver registration.

## Risks
Error metadata interpretation differs by CCF version and T1040 variant. Logging is rate-limited, which protects the system but can hide repeated unique errors. Clearing by writing `errdet` means diagnostic state is consumed by the handler. No PM restore exists if interrupt enables reset.

## Test Signals
Injectable fabric errors should produce critical logs with `errdet`, `cecar`, `cecar2`, address, and source id. Probe tests should cover both compatibles and T1040 BRR detection. Remove should clear interrupt enable paths for both versions.

# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/Kconfig

## Purpose
This Kconfig file gates the OMAP2+ fbdev display stack and includes the nested omapfb Kconfig only when Open Firmware and an OMAP2+/compile-test target are available.

## Important APIs, Types, And Functions
- The top-level conditional is `if OF && (ARCH_OMAP2PLUS || COMPILE_TEST)`.
- It sources `drivers/video/fbdev/omap2/omapfb/Kconfig`.

## Control Flow
Kconfig evaluation enters the nested OMAP2 omapfb menu only under the conditional.

## State And Persistence
No runtime state. It affects build configuration.

## Dependencies And Integration Points
It integrates the OMAP2 fbdev tree into the broader kernel config system and prevents non-DT/non-OMAP builds from seeing irrelevant options except through `COMPILE_TEST`.

## Risks
Disabling `OF` hides all nested options even if source files could compile. Path correctness must match the kernel tree layout.

## Test Signals
`menuconfig` should expose OMAP2 framebuffer options on OF-capable OMAP2+ or compile-test builds.

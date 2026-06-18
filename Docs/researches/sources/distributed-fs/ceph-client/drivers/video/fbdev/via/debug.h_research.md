# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/debug.h

## Purpose
`debug.h` provides compile-time debug and warning print macros for the VIA framebuffer driver.

## Important APIs, Types, And Data
The header defines `VIAFB_DEBUG` and `VIAFB_WARN` switches, plus `DEBUG_MSG()` and `WARN_MSG()` macros. When enabled, the macros call `printk`; when disabled, they call `no_printk`, preserving format checking while avoiding runtime output.

## Control Flow
There is no runtime control flow beyond macro expansion. Call sites in VIA source files compile either to logging calls or to `no_printk` stubs depending on the constants.

## State And Persistence
No runtime state is stored. The file controls build-time logging behavior only.

## Dependencies And Integration Points
It includes `<linux/printk.h>` and is included by `global.h`, making the macros available broadly across VIA fbdev files.

## Risks
Both debug and warning switches default to `0`, so even `WARN_MSG()` call sites are suppressed unless the header is edited. This can hide diagnostics that might otherwise be expected in warning scenarios. Conversely, enabling the macros globally could produce noisy kernel logs from register-heavy paths.

## Test Signals
Signals are compile-time: format warnings should still be caught through `no_printk`, enabling either macro should produce expected log output, and disabled builds should not emit runtime messages from `DEBUG_MSG()`/`WARN_MSG()` call sites.

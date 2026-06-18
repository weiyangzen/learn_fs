<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/debug.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/debug.h

## Purpose
`debug.h` is the small DWC2 debugfs interface header. It exposes debugfs lifecycle hooks to the rest of the driver while compiling them out cleanly when `CONFIG_DEBUG_FS` is disabled.

## Important APIs, types, and functions
When debugfs is enabled, it declares `dwc2_debugfs_init(struct dwc2_hsotg *hsotg)` and `dwc2_debugfs_exit(struct dwc2_hsotg *hsotg)`. When disabled, it provides inline stubs returning `0` or doing nothing. It includes `core.h` for the `dwc2_hsotg` declaration.

## Control flow
Callers can unconditionally call debugfs init/exit during probe/remove. The preprocessor selects real debugfs code or no-op stubs. This keeps platform and core code free of repeated `#ifdef CONFIG_DEBUG_FS` blocks.

## State and persistence behavior
The header stores no state. In enabled builds, state lives in `hsotg->debug_root` and `hsotg->regset` as created by `debugfs.c`; in disabled builds no debugfs state exists.

## Dependencies and integration points
It integrates the platform/core probe path with `debugfs.c`, `core.h`, and Linux `CONFIG_DEBUG_FS`. It also mirrors the DWC2 Makefile condition that only links `debugfs.o` when debugfs support is enabled.

## Risks
The main risk is signature drift between stubs and real functions, which would compile in one configuration and fail in another. Stub success can hide missing debugfs coverage in tests if only return values are checked.

## Test signals
Build DWC2 with `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n`. Runtime debugfs-enabled tests should confirm per-controller debug directories appear and are removed; debugfs-disabled tests should confirm probe/remove still succeed without unresolved symbols or conditional logic failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/debug.h -->

# sources/distributed-fs/ceph-client/sound/parisc/Kconfig

## Purpose

This Kconfig file defines PA-RISC GSC sound-driver configuration. It gates the PA-RISC sound submenu behind GSC bus support and exposes the Harmony/Vivace driver option.

## Important APIs, Types, and Functions

The top-level symbol is `SND_GSC`, a boolean `menuconfig` depending on `GSC` and defaulting to `y`. Inside `if SND_GSC`, `SND_HARMONY` is a tristate option named "Harmony/Vivace sound chip" and selects `SND_PCM`.

## Control Flow

Kconfig evaluation first hides all entries unless `GSC` is available. When `SND_GSC` is enabled, `SND_HARMONY` can be built in, modular, or disabled. Selecting Harmony automatically pulls ALSA PCM support, matching `harmony.c`'s PCM-only runtime interface.

## State and Persistence

The file only defines build-time configuration symbols. Its state persists in kernel `.config` and module build products, not at runtime.

## Dependencies and Integration Points

It integrates with the ALSA PA-RISC Makefile, where `CONFIG_SND_HARMONY` builds `snd-harmony.o`. It also depends on architecture bus discovery through `GSC`.

## Risks and Edge Cases

`SND_GSC` defaults to `y` whenever `GSC` exists, so Harmony can become visible by default on PA-RISC configs. The Harmony option does not explicitly depend on `PARISC`, relying on `GSC` to constrain architecture. Missing `SND_PCM` select would break the driver, but it is present.

## Test Signals

Run Kconfig coverage for PA-RISC/GSC enabled and disabled configs, verify `CONFIG_SND_HARMONY=m` produces `snd-harmony.ko`, and verify `SND_PCM` is selected automatically.

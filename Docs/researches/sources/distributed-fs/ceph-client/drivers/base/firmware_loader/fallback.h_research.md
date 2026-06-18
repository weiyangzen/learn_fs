# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback.h

## Purpose
`fallback.h` declares firmware fallback entry points and provides no-op stubs when sysfs fallback or platform fallback support is disabled.

## Important APIs, Types, And Functions
It declares `firmware_fallback_sysfs()`, `kill_pending_fw_fallback_reqs()`, `fw_fallback_set_cache_timeout()`, `fw_fallback_set_default_timeout()`, and `firmware_fallback_platform()`, plus inline stubs returning the original error or `-ENOENT`.

## Control Flow, State, And Persistence
The header preserves call-site simplicity: main firmware loading code can call fallback functions unconditionally and receive either real behavior or a compile-time stub. Platform fallback is similarly gated by `CONFIG_EFI_EMBEDDED_FIRMWARE`.

## Dependencies, Integration Points, Risks, And Test Signals
It depends on `firmware.h` and `sysfs.h`, so it connects the core state machine with fallback-specific devices. Risks are mostly build-configuration mismatches: stubs must preserve original errors and not accidentally enable fallback semantics. Test signals are compile coverage with user-helper off, EFI embedded firmware off, both enabled, and direct lookup failures preserving errno when fallback is not built.

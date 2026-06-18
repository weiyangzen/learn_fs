# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/leds.h

## Purpose

`leds.h` declares the optional ath10k LED integration API and provides no-op inline fallbacks when LED support is disabled. It lets the rest of the driver call LED registration/start/unregistration unconditionally.

## Important APIs, Types, and Functions

- With `CONFIG_ATH10K_LEDS`: declares `ath10k_leds_unregister(struct ath10k *ar)`, `ath10k_leds_start(struct ath10k *ar)`, and `ath10k_leds_register(struct ath10k *ar)`.
- Without `CONFIG_ATH10K_LEDS`: defines inline no-op `ath10k_leds_unregister()` and inline success-returning `ath10k_leds_start()` / `ath10k_leds_register()`.
- Includes `core.h` for `struct ath10k`.

## Control Flow

The only control flow is compile-time. The preprocessor selects real declarations when LED support is enabled and inline stubs otherwise. Runtime callers do not need their own `#ifdef CONFIG_ATH10K_LEDS` guards.

## State and Persistence Behavior

The header has no state. In the disabled configuration, no LED state is allocated or registered by these functions. In the enabled configuration, state is managed by `leds.c` through `ar->leds`.

## Dependencies and Integration Points

This header is included by ath10k core/startup code that wants to call LED helpers independent of Kconfig. It depends on the build system providing `CONFIG_ATH10K_LEDS` and on `core.h` defining `struct ath10k` and LED-related members under the matching configuration.

## Risks

- Stub functions return success, so disabled LED support is intentionally indistinguishable from unsupported/no-op LED hardware to callers.
- Any caller expecting side effects from `ath10k_leds_start()` must remember that those effects vanish when the config is disabled.
- Header and `core.h` configuration guards must stay synchronized so `ar->leds` members are present when real functions are compiled.

## Test Signals

The main signals are successful builds with `CONFIG_ATH10K_LEDS=y` and `n`, no unresolved symbols in either mode, startup/register paths working without local `#ifdef`s, and no LED class device appearing when support is disabled.

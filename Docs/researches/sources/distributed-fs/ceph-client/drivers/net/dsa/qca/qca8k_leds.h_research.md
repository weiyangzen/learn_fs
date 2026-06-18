# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k_leds.h

## Purpose

This header provides the conditional interface for QCA8K LED setup. It allows the main QCA8K setup path to call `qca8k_setup_led_ctrl()` regardless of whether LED support is compiled in.

## Important APIs, Types, and Functions

- When `CONFIG_NET_DSA_QCA8K_LEDS_SUPPORT` is enabled, it declares `int qca8k_setup_led_ctrl(struct qca8k_priv *priv);`.
- Otherwise it defines a static inline stub returning 0.

## Control Flow

The header itself has no runtime control flow. At compile time it selects either the real LED setup function or the no-op fallback. `qca8k_setup()` can therefore call the function unconditionally and treat LED support as optional.

## State and Persistence

The header introduces no state. With LED support disabled, no LED class devices or LED hardware configuration are created by this interface.

## Dependencies and Integration Points

It depends on `struct qca8k_priv` being visible to callers through `qca8k.h`. The real implementation lives in `qca8k-leds.c`, included by the Makefile only when the same Kconfig symbol is enabled.

## Risks and Edge Cases

The Kconfig, Makefile, and header condition must remain aligned. If the C file is built without the declaration or the declaration exists without the object, build failures can result. The no-op stub makes systems without LED support silently skip LED initialization, which is expected but should be considered when diagnosing missing LED devices.

## Test Signals

Build QCA8K with LED support enabled and disabled. Enabled builds should link against `qca8k-leds.o`; disabled builds should compile with the inline stub and still probe switches successfully.

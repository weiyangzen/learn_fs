# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/Kconfig

## Purpose

This Kconfig file exposes build-time options for Qualcomm/Atheros DSA switch drivers in this directory: the AR9331 embedded switch, the QCA8K family driver, and optional QCA8K LED support.

## Important APIs, Types, and Functions

- `NET_DSA_AR9331` is a tristate option that depends on `NET_DSA` and selects `NET_DSA_TAG_AR9331` and `REGMAP`.
- `NET_DSA_QCA8K` is a tristate option that selects the QCA DSA tagger and `REGMAP`.
- `NET_DSA_QCA8K_LEDS_SUPPORT` is a bool depending on `NET_DSA_QCA8K`, compatible LED class linkage, and `LEDS_TRIGGERS`.

## Control Flow

There is no runtime control flow. The file controls Kconfig dependency resolution. Enabling AR9331 or QCA8K makes the corresponding object buildable; LED support is compiled into the QCA8K composite object only when the LED option is enabled.

## State and Persistence

State is limited to kernel configuration values. Those values persist in the generated `.config` and determine which object files and tag protocol helpers are included.

## Dependencies and Integration Points

The options integrate with the DSA subsystem, DSA tag protocol modules (`tag_ar9331`, `tag_qca`), regmap, and the LED subsystem. `NET_DSA_QCA8K_LEDS_SUPPORT` explicitly handles built-in/module compatibility by allowing `LEDS_CLASS=y` or `LEDS_CLASS=NET_DSA_QCA8K`.

## Risks and Edge Cases

Incorrect dependencies can produce link failures, especially for LED class symbols or tagger support. The help text for LED support says "This enabled support" rather than "enables"; cosmetic only. QCA8K does not explicitly depend on `NET_DSA` in this file, so it relies on its menu context or higher-level DSA Kconfig inclusion to make the option meaningful.

## Test Signals

Build matrix signals include `NET_DSA_AR9331=m/y`, `NET_DSA_QCA8K=m/y`, LED support built in and disabled, and module/built-in combinations for `LEDS_CLASS`. Runtime signals are availability of matching DSA taggers and absence of unresolved symbols.

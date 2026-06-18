# sources/distributed-fs/ceph-client/drivers/dpll/Kconfig

## Purpose

This Kconfig fragment declares the generic DPLL subsystem configuration menu. It defines the base `CONFIG_DPLL` symbol, the optional debug-oriented `CONFIG_DPLL_REFCNT_TRACKER`, and includes vendor-specific DPLL driver configuration from `drivers/dpll/zl3073x/Kconfig`.

## Important Symbols

`config DPLL` is a bool with no prompt in this file, intended to be selected by DPLL providers or users rather than directly exposed. `config DPLL_REFCNT_TRACKER` is user-visible, depends on `DEBUG_KERNEL`, `STACKTRACE_SUPPORT`, and `DPLL`, and selects `REF_TRACKER`. Its help text documents debugfs paths under `/sys/kernel/debug/ref_tracker/dpll_device_*` and `/sys/kernel/debug/ref_tracker/dpll_pin_*`.

## Control Flow and Integration

The file opens a `menu "DPLL device support"`, defines the generic symbols, sources the ZL3073x child Kconfig, and closes the menu. Build behavior is consumed by the DPLL Makefile: `CONFIG_DPLL` controls compilation of the generic DPLL core/netlink objects, while `CONFIG_DPLL_REFCNT_TRACKER` controls conditional ref tracker calls in `dpll_core.c`.

## State and Persistence

Kconfig selections persist in the kernel build configuration, not at runtime. Enabling the tracker changes runtime behavior by allocating/freeing ref-tracker records for DPLL devices and pins, but the Kconfig file itself has no runtime state.

## Risks and Test Signals

The base symbol being promptless means driver Kconfig files must select or depend on it correctly; otherwise DPLL providers can fail to link or omit the core. The tracker option depends on debug facilities and should be tested by building with and without `CONFIG_DPLL_REFCNT_TRACKER`, checking that DPLL core references to ref tracking compile away cleanly when disabled and expose debugfs leak data when enabled.

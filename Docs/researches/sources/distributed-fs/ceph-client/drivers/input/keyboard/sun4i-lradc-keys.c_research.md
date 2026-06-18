# sources/distributed-fs/ceph-client/drivers/input/keyboard/sun4i-lradc-keys.c

## Purpose

This platform driver reports keys connected to Allwinner LRADC channel 0 through a resistor ladder. It converts ADC readings to voltages using the regulator voltage and SoC-specific divisor, selects the closest configured key voltage, and reports one active key at a time.

## Important APIs, Types, and Functions

`struct lradc_variant` describes voltage divisor and optional clock/reset requirements. `struct sun4i_lradc_data` stores device/input, MMIO, optional clock/reset, VREF regulator, keymap, active keycode, and computed VREF. `sun4i_lradc_load_dt_keymap()` parses child nodes with `channel`, `voltage`, and `linux,code`. `sun4i_lradc_open()` powers/configures LRADC. `sun4i_lradc_irq()` handles keyup/keydown interrupts and voltage matching.

## Control Flow

Probe loads the DT keymap, selects variant data, acquires optional clock/reset for newer variants, gets the `vref` regulator, allocates input, maps MMIO, requests IRQ, registers input, and optionally configures wake IRQ. Opening enables regulator, reset, clock, computes effective VREF, programs sample/debounce control, and enables keyup/keydown interrupts. On keydown with no cached key, the handler reads 6-bit ADC data, computes voltage, chooses the closest configured key, reports press, and caches the keycode. On keyup it releases the cached key.

## State and Persistence Behavior

The cached `chan0_keycode` is required because release interrupts do not identify which key was released. The computed VREF is refreshed on open, reflecting current regulator voltage. Hardware is fully disabled on close, including IRQ mask, clock, reset, and regulator.

## Dependencies and Integration Points

The driver depends on OF child keymap nodes, platform MMIO/IRQ, regulators, optional clocks/resets, `dev_pm_set_wake_irq()`, and Allwinner compatible variants for A10, A83T R-LRADC, and R329 LRADC.

## Risks and Edge Cases

Only channel 0 is supported; child nodes for other channels are rejected. Closest-voltage matching has no tolerance threshold, so noisy or misconfigured resistor ladders can report the wrong key. If `chan0_keycode` is zero and a keyup arrives, keycode zero is released. Optional clock/reset pointers are NULL for older variants and rely on helper APIs accepting NULL.

## Test Signals

Test DT keymap validation, voltage matching under varied VREFs, noisy ADC values, keydown while a key is cached, keyup release, regulator/clock/reset failure unwind, wake IRQ setup, all compatible variants, and open/close power sequencing.

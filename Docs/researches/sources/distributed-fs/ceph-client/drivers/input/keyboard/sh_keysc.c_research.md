# sources/distributed-fs/ceph-client/drivers/input/keyboard/sh_keysc.c

## Purpose

This platform driver supports the SuperH KEYSC matrix keypad controller. It uses board-provided `struct sh_keysc_info` to select a hardware scan mode, scan timing, keycodes, and debounce delays, then reports matrix key events through the input subsystem.

## Important APIs, Types, and Functions

`struct sh_keysc_priv` stores the MMIO base, last-key bitmap, input device, and copied platform data. `sh_keysc_mode[]` maps controller modes to keyout/keyin counts and KYMD values. `sh_keysc_read()` and `sh_keysc_write()` access 16-bit registers. `sh_keysc_level_mode()` arms level IRQ mode. `sh_keysc_isr()` performs the full matrix scan, debouncing/intersection logic, and event reporting. Probe/remove manually allocate and tear down resources.

## Control Flow

Probe requires platform data, MMIO resource, and IRQ, maps registers, allocates input, requests a threaded IRQ, sets key capabilities, registers input, enables runtime PM, programs KYCR1, enters level mode, and enables wakeup. The ISR disables IRQ generation, drives each output line low, reads input lines, accumulates repeated scan results into `keys0` and `keys1`, restores level mode, and loops while the controller indicates pending activity. It then compares with `last_keys` and emits press/release events.

## State and Persistence Behavior

`last_keys` tracks currently reported keys. Platform data is copied into driver state so board data persists after probe. Runtime PM is held active after probe and released on remove or non-wakeup suspend. Suspend can set a wake bit in KYCR1 and enable IRQ wake.

## Dependencies and Integration Points

It depends on legacy platform data (`linux/input/sh_keysc.h`), platform IRQ/MMIO resources, runtime PM, and SuperH KEYSC register semantics. There is no DT parser in this file.

## Risks and Edge Cases

Manual allocation and cleanup increase unwind risk compared with devm-managed drivers. Invalid platform mode values could index outside `sh_keysc_mode[]` unless board data is trusted. The scan algorithm is timing-sensitive (`delay`, `kycr2_delay`) and may misreport on boards with slow lines. Wake/runtime PM behavior assumes the controller remains configured across low-power transitions.

## Test Signals

Test each KEYSC mode, invalid or missing platform data, IRQ scan with simultaneous keys, release detection, timing extremes, runtime PM suspend/resume with and without wakeup, remove cleanup after registered input, and keycode arrays containing zero/reserved entries.

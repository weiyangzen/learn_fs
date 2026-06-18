# sources/distributed-fs/ceph-client/drivers/rtc/rtc-at91rm9200.c

## Purpose

`rtc-at91rm9200.c` drives the Atmel/Microchip AT91 RTC peripheral family. It provides BCD time/calendar registers, alarm registers, update synchronization, optional correction offset on newer variants, shared IRQ handling, and suspend wake event caching.

## Important APIs, types, and functions

`struct at91_rtc_config` selects shadow IMR and correction support. Global state tracks mapped registers, IRQ, slow clock, completions `at91_rtc_updated` and `at91_rtc_upd_rdy`, shadow interrupt mask, suspend state, and cached events. RTC callbacks include `at91_rtc_readtime()`, `at91_rtc_settime()`, `at91_rtc_readalarm()`, `at91_rtc_setalarm()`, `at91_rtc_alarm_irq_enable()`, and on SAMA5-class devices `at91_rtc_readoffset()` and `at91_rtc_setoffset()`.

## Control flow

Probe maps MMIO, enables the slow clock, forces 24-hour mode, disables all interrupts, requests a shared conditional-suspend IRQ, enables wake capability, selects ops based on correction support, sets range 1900-2099, registers the RTC, and enables second events so the update-ready completion can initialize. Setting time waits for update readiness, requests calendar/time update mode, enables ACKUPD IRQ, waits for acknowledgement, writes BCD time/calendar registers, clears second event, leaves update mode, and enables second-event IRQ again. IRQ handling reads status masked by IMR/shadow IMR, completes update waiters, clears status, reports or caches RTC events depending on suspend state.

## State and persistence behavior

Hardware persists time/calendar, alarm, mode/correction, interrupt masks, and status. Driver state is mostly global because this old driver assumes one device. During suspend, enabled alarm/second events are cached and replayed on resume if wake-capable.

## Dependencies and integration points

It depends on platform MMIO and IRQ, common clock API, BCD and bitfield helpers, completions, spinlocks, RTC class APIs, PM suspend helpers, and OF compatibles for AT91RM9200, AT91SAM9x5, SAMA5D4/D2, and SAM9X60.

## Risks and edge cases

Global singleton state prevents multiple independent instances. Shadow IMR is a workaround for unreliable IMR reads and must stay synchronized with IER/IDR writes. `at91_rtc_decodetime()` returns full year before the caller subtracts 1900; alarm year is intentionally invalid because hardware lacks it. Offset conversion has low/high correction modes and rejects large values. Shared IRQ and suspend caching require careful ordering to avoid lost wake events.

## Test signals

Test set-time synchronization with ACKUPD, alarm matching and readback with missing year, correction read/set on SAMA5-class compatibles, shadow IMR behavior, shared IRQ rejection when status is not ours, suspend wake caching and replay, and cleanup paths disabling interrupts and clocks.

# sources/distributed-fs/ceph-client/include/linux/mfd/syscon/atmel-st.h

## Purpose

This 45-line header defines AT91 system timer register offsets and bitfields for watchdog, periodic interval, real-time timer, status, interrupt, alarm, and current counter access.

## Important APIs, Types, and Functions

It exports `AT91_ST_CR`, `PIMR`, `WDMR`, `RTMR`, `SR`, `IER`, `IDR`, `IMR`, `RTAR`, and `CRTR` offsets, plus masks for watchdog restart, interval value, watchdog reset/external signal enables, real-time prescaler, status bits, alarm value, and current real-time value.

## Control Flow

No executable flow. Timer/watchdog/RTC-like code uses these constants to configure intervals, kick watchdog, enable interrupts, and read status/counter registers.

## State and Persistence Behavior

System timer and watchdog configuration persists in hardware and can trigger interrupts or reset events.

## Dependencies and Integration Points

It integrates AT91 syscon/timer/watchdog users through shared register definitions.

## Risks and Edge Cases

Watchdog restart/reset bits are high impact. Alarm and counter fields are limited width, so wraparound handling belongs in consumers.

## Test Signals

Timer interrupt tests, watchdog kick/reset tests, alarm wrap tests, and compile coverage for AT91 system timer users.

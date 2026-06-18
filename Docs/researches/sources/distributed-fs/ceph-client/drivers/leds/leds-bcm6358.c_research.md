# sources/distributed-fs/ceph-client/drivers/leds/leds-bcm6358.c

## Purpose
Implements memory-mapped serial LED control for Broadcom BCM6358 controllers. It exposes firmware child nodes as basic LED class devices with active-low and default-state support.

## Important APIs, Types, And Functions
`struct bcm6358_led` stores classdev, MMIO base, shared spinlock, pin, and active-low flag. Main functions are endian-aware register read/write helpers, `bcm6358_led_busy`, `bcm6358_led_set`, `bcm6358_led`, and `bcm6358_leds_probe`.

## Control Flow
Probe maps MMIO, allocates a spinlock, waits for the serial LED controller to be idle, configures polarity and clock divider from DT, writes the control register, then iterates child nodes. Each valid child `reg` below 32 creates a classdev, reads default state from firmware, applies it to hardware, assigns brightness callback, and registers through devm.

Brightness waits for the busy bit to clear, reads the mode register, sets or clears the pin bit based on brightness and active-low polarity, and writes the mode register under the spinlock.

## State And Persistence
The driver has no cached per-LED hardware state beyond classdev brightness; the controller mode register is the source of truth for `default-state = keep`. Hardware control register settings persist until overwritten.

## Dependencies And Integration Points
Depends on platform MMIO, OF child nodes, LED class, spinlocks, delay loops, and endian handling. Compatible is `brcm,bcm6358-leds`.

## Risks
`bcm6358_led_busy` spins with `udelay` until the busy bit clears and has no timeout, so stuck hardware can hang the caller. No hardware blink support is exposed. Shared mode register read-modify-write depends on spinlock coverage.

## Test Signals
Validate clock divider and polarity DT parsing, registration of valid child pins, rejection/warning of invalid pins, default-state keep/on/off, active-low writes, and behavior when the busy bit clears before writes.

# sources/distributed-fs/ceph-client/include/linux/mfd/si476x-platform.h

## Purpose

This 258-line header defines platform data, pinmux configuration, oscillator/power-up arguments, and phase diversity modes for Si476x radio tuners.

## Important APIs, Types, and Functions

It defines four selectable I2C addresses, enums for IQ, digital audio, IC link, analog audio, INTB/A1 pin functions, `struct si476x_pinmux`, oscillator bias/start/frequency/mode enums, `enum si476x_func`, `struct si476x_power_up_args`, `enum si476x_phase_diversity_mode`, and `struct si476x_platform_data`.

## Control Flow

No executable flow exists. Platform or device-tree data is converted into `si476x_platform_data`; core startup passes `power_up_parameters` to the POWER_UP command and configures pins through command helpers declared in `si476x-core.h`.

## State and Persistence Behavior

The structures store boot-time configuration for reset GPIO, power-up mode, oscillator settings, pin muxing, and diversity role. Hardware pin/function state persists while the tuner remains powered.

## Dependencies and Integration Points

It integrates board data with Si476x MFD core, command layer, audio interfaces, IRQ routing, IQ output, and multi-tuner diversity setups.

## Risks and Edge Cases

Pin function enum values are command ABI values, not arbitrary indexes. Wrong oscillator frequency or xmode can prevent boot. Diversity roles must match physical tuner wiring.

## Test Signals

Platform-data parsing tests, POWER_UP argument encoding tests, pin configuration command tests, I2C address probe tests, and diversity-mode hardware tests.

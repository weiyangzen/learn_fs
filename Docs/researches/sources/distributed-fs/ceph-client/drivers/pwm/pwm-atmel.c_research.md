# sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel.c

Purpose: implements the main Atmel/Microchip PWM controller driver for SoCs with dedicated PWM channel registers.

Important APIs/types/functions: `struct atmel_pwm_chip` stores clock, MMIO base, variant register layout, and an `update_pending` bitmask. Variant data describes v1/v2 duty/period/update registers and period width. Helpers calculate period/prescaler (`atmel_pwm_calculate_cprd_and_pres()`), duty (`atmel_pwm_calculate_cdty()`), pending-update handling, disable waits, and clock enable restoration. `atmel_pwm_apply()` and `atmel_pwm_get_state()` are the callbacks.

Control flow: probe allocates four PWMs, maps registers, gets a prepared clock, enables the clock once for already-running hardware channels, and registers the chip. Apply can update duty in-place when enabled polarity and period are unchanged; otherwise it disables a running channel, enables the clock for a stopped one, programs CMR/CPRD/CDTY, and enables the channel. Disable waits for pending duty updates and hardware disable before optionally disabling the clock.

State and persistence: requested state is cached by the PWM core; driver state tracks pending hardware update events and variant layout. Hardware state may be inherited at boot, and probe keeps clocks enabled for channels already active.

Dependencies and integration: depends on MMIO, clock framework, OF match data for Atmel/SAMA5/SAM9x60 variants, and PWM core debug/state callbacks.

Risks and test signals: pending-update waiting uses polling with a two-second timeout; missed ISR-clearing semantics can affect disable correctness. Disabled polarity changes are documented as not honored. Clock reference counting across already-on channels must match channel activity. Test signals include v1/v2 variants, duty-only update path, zero/full duty, disable after pending update, `get_state` after bootloader configuration, and clock-count balance on probe failure.

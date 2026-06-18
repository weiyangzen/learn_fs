## sources/distributed-fs/ceph-client/include/linux/mfd/atmel-hlcdc.h

Purpose: This header defines the shared Atmel HLCDC/XLCDC MFD register bits and parent state used by display, PWM, and other HLCDC child drivers.

Important APIs, types, and constants: Register macros cover configuration slots, signal polarity/dither/guard timing, enable/disable/status/IRQ registers, XLCDC attribute update bits, clock selection/divider fields, block enable bits for pixel/sync/display/PWM/SIP/XLCDC blocks, and interrupt/status bits including start-of-frame, sync disable, FIFO error, and layer status. `struct atmel_hlcdc` stores the shared regmap, optional LVDS PLL clock, peripheral/system/slow clocks, and IRQ.

Control flow: The header has no functions. Parent probe initializes regmap and clocks, then child drivers use the shared `atmel_hlcdc` object to enable clocks, configure display timing or PWM functions, and handle IRQ status.

State and persistence: Hardware registers hold display signal configuration, block enable state, clock dividers, and interrupt state. Clock framework references are runtime kernel state and are not persistent.

Dependencies and integration points: Includes `linux/clk.h` and `linux/regmap.h`; integrates with DRM/display, PWM, clock framework, IRQ handling, and MFD child registration.

Risks: Clock divider macro `ATMEL_HLCDC_CLKDIV(div)` assumes a valid divider greater than or equal to two. HLCDC vs XLCDC bit layouts differ for mode and attribute update masks. Misprogrammed polarity or guard timing creates display sync faults rather than clean probe failures.

Test signals: Build child display/PWM drivers, verify clocks are acquired and prepared, confirm regmap writes to enable blocks and configure timings, exercise IRQ status handling for SOF/FIFO errors, and test both HLCDC and XLCDC-compatible hardware.

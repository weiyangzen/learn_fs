# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dibx000_common.h

## Purpose
`dibx000_common.h` defines shared data structures, constants, and prototypes used by DiBcom demodulator drivers. It covers demod-hosted I2C master state, tuner band classification, AGC/PLL configuration tables, ADC power states, output/input modes, tuning state machine IDs, frontend channel-status context, GPIO/subband board functions, and TIMF commands.

## Important APIs, Types, and Functions
`enum dibx000_i2c_interface` names tuner and GPIO-based I2C interfaces. `struct dibx000_i2c_master` stores child adapters, parent I2C information, base register, buffers, messages, and a mutex. Prototypes expose `dibx000_init_i2c_master()`, `dibx000_get_i2c_adapter()`, `dibx000_exit_i2c_master()`, `dibx000_reset_i2c_master()`, and `dibx000_i2c_set_speed()`. `struct dibx000_agc_config` and `struct dibx000_bandwidth_config` describe board-specific RF gain and clock/PLL/timing parameters. `enum frontend_tune_state` defines multi-phase tuner, AGC, and demod states. `struct dvb_frontend_parametersContext`, `struct dibGPIOFunction`, and `struct dibSubbandSelection` define shared firmware/board abstractions.

## Control Flow
The header is included by concrete demod drivers and board code. Config tables are selected by frequency band using `BAND_OF_FREQUENCY()`, I2C adapters are requested by interface/gating mode, and tune-state constants coordinate staged demod control loops in implementation files.

## State and Persistence
This file declares runtime state layouts but does not allocate storage. State is held by embedding drivers and by hardware registers programmed through the common implementation. There is no durable persistence.

## Dependencies and Integration Points
It requires Linux I2C and DVB frontend definitions through includers. It integrates DiB8000/DiB9000 and related demods with tuner drivers, board GPIO policy, PLL/AGC tables, and DVB frontend property/tune state handling.

## Risks and Edge Cases
`BAND_OF_FREQUENCY()` is an inline macro with a nonmonotonic first two comparisons: frequencies less than or equal to 170000 kHz classify as CBAND before the FM threshold check, so callers must understand the intended legacy mapping. Many structures contain raw pointers to config tables that need stable lifetime. Output mode constants are shared across chips but not every chip implements every mode. Numeric tune/status values are negative sentinel codes and should not be mixed with Linux errno without care.

## Test Signals
Compile coverage across DiB demod drivers, I2C adapter selection for all interfaces, AGC/PLL table selection by band, GPIO/subband application, tune-state transitions, bandwidth conversion macros, and status-code handling are the important signals.

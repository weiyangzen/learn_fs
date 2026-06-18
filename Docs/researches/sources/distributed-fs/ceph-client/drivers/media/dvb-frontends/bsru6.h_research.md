# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsru6.h

Purpose: Provides static demod initialization and tuner programming helpers for ALPS BSRU6 DVB-S hardware using an STV0299 demodulator.

Important APIs/types/functions: `alps_bsru6_inittab` is the STV0299 register initialization table. `alps_bsru6_set_symbol_rate()` selects ACLK/BCLK values across symbol-rate ranges and writes the ratio registers. `alps_bsru6_tuner_set_params()` computes a rounded 125 kHz PLL divider, sends four bytes to tuner I2C address `0x61`, and switches a control byte for high-band frequencies above 1530 MHz. `alps_bsru6_config` sets demod address, clock, inversion, lock-output and voltage-output options, delay, and symbol-rate callback.

Control flow: Included board code passes `alps_bsru6_config` to `stv0299_attach()` and wires the tuner helper into frontend ops. Tune parameter flow validates satellite IF range, computes divider/control bytes, opens the demod I2C gate if present, and sends the tuner I2C transfer.

State and persistence: Header data is static initialization state only; no long-lived mutable state is owned. Register programming is volatile.

Dependencies/integration: Depends on STV0299 register helpers and DVB/I2C types from includers. Used by TTPci budget/budget-ci boards.

Risks and test signals: Validate table termination, symbol-rate thresholds, low/high-band control bytes, rounded divider math, frequency limits, and I2C transfer failure. As with `bsbe1.h`, I2C gate closure is not explicit in the helper and must be verified in board integration.

# sources/distributed-fs/ceph-client/arch/m68k/atari/debug.c

Purpose: early Atari debug console output over MFP serial, SCC serial, MIDI ACIA, or parallel printer.

Important APIs are early parameter handler `atari_debug_setup()` and initialization helpers `atari_init_mfp_port()`, `atari_init_scc_port()`, and `atari_init_midi_port()`. It exports `atari_SCC_reset_done` so kgdb or other code can prevent duplicate SCC reset.

Control flow: `debug=ser` maps to SCC on Falcon and MFP otherwise; explicit `ser1`, `ser2`, `midi`, and `par` choose output backends. Each backend supplies a `console.write` method that polls device transmit readiness and inserts carriage returns before newlines. Parallel output initializes PSG ports and disables BUSY interrupts, then times out if no printer responds.

State is the `atari_console_driver.write` callback, `atari_SCC_reset_done`, and hardware serial/parallel register configuration. SCC initialization writes many channel B registers with required delays and marks reset complete.

Dependencies include Atari hardware and interrupt headers, early console registration, termios baud constants, `loops_per_jiffy`, and `atari_switches`. Integration is through `early_param("debug", ...)`, allowing logs before full serial drivers bind.

Risks and test signals: polling can hang if readiness bits never change, so parallel has a timeout but serial paths do not. Validate `debug=ser1`, `ser2`, `midi`, and `par` output, Falcon default routing, and kgdb coexistence with `atari_SCC_reset_done`.

# sources/distributed-fs/ceph-client/sound/soc/codecs/arizona.h

Purpose: public shared header for Arizona-family ASoC codec support. It defines clock/FLL constants, shared private data structures, DAPM/control/route construction macros, exported tables, and prototypes consumed by chip-specific Arizona codec drivers and jack support.

Important APIs and types: `struct arizona_dai_priv` stores each DAI clock source and PCM rate constraint. `struct arizona_priv` aggregates ADSP instances, parent MFD pointer, SYSCLK/ASYNCCLK rates, DAI private state, input/output DAPM pending counters, DVFS lock/request/cache state, and jack-detection state used by `arizona-jack.c`. `struct arizona_fll` stores FLL identity, base register, VCO multiplier, output, sync/ref sources and frequencies, plus IRQ names. The header declares exported helpers from `arizona.c` for DAPM events, FLL, DVFS, common init, DAI ops, output mode, notifier registration, DT parsing, and jack probing.

Control flow encoded by macros: `ARIZONA_GAINMUX_CONTROLS`, `ARIZONA_MIXER_CONTROLS`, mux enum macros, `ARIZONA_MUX_WIDGETS`, `ARIZONA_MIXER_WIDGETS`, `ARIZONA_DSP_WIDGETS`, and route macros allow chip drivers to build large consistent DAPM graphs while reusing the shared mixer source tables. `ARIZONA_EQ_CONTROL` and `ARIZONA_LHPF_CONTROL` bind byte controls to the safe coefficient put handlers in `arizona.c`.

State and persistence: this header does not persist state itself, but it defines the in-memory state contract that chip drivers must allocate and attach as component drvdata. The jack-related fields persist detection progress across delayed works and IRQ handling. Clock/FLL fields persist current requested clocking so repeated set calls can be no-ops or validate active-clock changes.

Dependencies and integration points: includes Linux completion/notifier/MFD Arizona core headers, ASoC headers, and `wm_adsp.h`. It bridges chip-specific codecs, shared Arizona support, jack support, ADSP support, and the parent MFD notifier chain. Inline notifier helpers register with `arizona->notifier`.

Risks: macro-generated controls and routes depend on exact register spacing and naming conventions; mistakes in chip drivers using these macros can create broken or ambiguous DAPM graphs. `struct arizona_priv` is broad and shared by audio and jack code, so lifetime and initialization ordering are important. The inline notifier helpers assume component drvdata is an initialized `struct arizona_priv` with a valid parent.

Test signals: compile all Arizona codec users; inspect generated ALSA controls and DAPM routes; test notifier registration/unregistration; verify jack detection still works when codecs share this private state; validate that each chip driver initializes `arizona_init_dai`, DVFS, FLL, and jack fields before first use.

# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-demod.c

Purpose: DVB-T demodulator frontend implementation for the MaxLinear MxL111SF integrated demod. It exposes `dvb_frontend_ops` for tuning, TPS reporting, lock/status, signal strength, BER/SNR stubs, and uncorrected block counts while delegating register access to callbacks supplied by the USB bridge driver.

Important APIs/types/functions: `struct mxl111sf_demod_state` ties `struct dvb_frontend` to the shared `mxl111sf_state` and `mxl111sf_demod_config`. Callback wrappers are `mxl111sf_demod_read_reg()`, `mxl111sf_demod_write_reg()`, and `mxl111sf_demod_program_regs()`. TPS helpers read code rate, modulation, FFT mode, guard interval, and hierarchy from V6 registers. `mxl111sf_demod_set_frontend()` invokes tuner `set_params()`, applies a PHY PLL patch register sequence, and clears IRQ state. `mxl111sf_demod_attach()` allocates the frontend and is exported.

Control flow: the main USB driver calls `mxl111sf_demod_attach()` for DVB-T profiles, then later attaches the MxL111SF tuner. When users tune, DVB core calls `set_frontend()`, which first tunes RF through tuner ops, waits, programs the PLL patch through bridge callbacks, resets IRQ status, and waits again. Status reads sample RS, TPS, sync, and FEC bits and translate them into DVB frontend status flags; `get_frontend()` reads TPS fields and asks tuner ops for current bandwidth/frequency.

State and persistence: state is allocated per frontend and released by `mxl111sf_demod_release()`. The demod driver caches no lock counters other than frontend private state; hardware registers hold tune, TPS, error, SNR, and status values. BER/SNR calculations are disabled by default to avoid floating point in kernel code, so those metrics return zero-derived values.

Dependencies and integration: depends on `mxl111sf.h` for shared state/debug, `mxl111sf-reg.h` for register constants, and DVB frontend APIs. It is a bridge-attached module selected with `CONFIG_DVB_USB_MXL111SF` and relies on the USB driver for register transport and register programming.

Risks: many switch statements do not set defaults for invalid hardware encodings, so output fields may retain caller-provided values when register contents are unexpected. `read_signal_strength()` derives strength from a disabled SNR calculation unless the optional macro is enabled. `get_frontend()` ignores return codes from TPS helper calls. The PLL patch is hard-coded and globally applied for every tune.

Test signals: build/export symbol resolution; DVB-T attach and release; tune to 6/7/8 MHz channels through tuner ops; frontend status transitions for RS/TPS/sync/FEC lock bits; TPS field reads matching known broadcasts; `read_ucblocks()` scale behavior; no floating-point build warnings on all architectures.

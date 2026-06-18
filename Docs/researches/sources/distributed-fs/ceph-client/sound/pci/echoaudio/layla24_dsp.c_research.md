# sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla24_dsp.c

## Purpose

`layla24_dsp.c` implements Layla24-specific firmware/ASIC handling, GML control-register programming, continuous sample-rate mode, input clocking, and digital-mode ASIC switching.

## Important APIs, Types, and Functions

`init_hw()` validates Layla24, initializes the comm page, enables internal/S/PDIF/word/ADAT clocks, sets supported digital modes, and loads firmware. `load_asic()` loads the PCI-card ASIC and default external S/PDIF ASIC, then writes a 48 kHz internal GML control register. `set_sample_rate()` maps standard rates and uses `LAYLA24_CONTINUOUS_CLOCK` plus `DSP_VC_SET_LAYLA24_FREQUENCY_REG` for nonstandard rates. `set_input_clock()` handles internal, S/PDIF, word, and ADAT. `switch_asic()` swaps external ASIC images while preserving monitor state. `dsp_set_digital_mode()` selects S/PDIF RCA, S/PDIF optical, or ADAT and switches ASICs as needed.

## Control Flow

Initialization loads DSP, base ASIC, and default external ASIC. Rate changes either update fixed clock bits or program the frequency register before writing the GML control register. Digital-mode changes may first force internal 48 kHz, then sleep while switching ASIC firmware, then take the spinlock to update the control register.

## State and Persistence Behavior

Persistent fields include `asic_code`, `digital_mode`, `input_clock`, `sample_rate`, auto-mute/pro S/PDIF state, and monitor matrix. `switch_asic()` temporarily mutes the monitor matrix during firmware load and restores it afterward.

## Dependencies and Integration Points

It depends on `echoaudio_gml.c`, shared DSP loader helpers, Layla24 ASIC firmware files, and ALSA clock/digital-mode controls.

## Risks and Test Signals

Risks include sleeping under the wrong lock, losing monitor levels during ASIC switch, bad continuous-rate divisor math, and invalid double-speed ADAT states. Test signals are ASIC switch success, monitor persistence across S/PDIF/ADAT changes, clock detection, nonstandard rate playback, and no handshake errors.

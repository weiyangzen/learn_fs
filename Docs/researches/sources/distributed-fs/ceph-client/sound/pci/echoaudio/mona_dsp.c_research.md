# sources/distributed-fs/ceph-client/sound/pci/echoaudio/mona_dsp.c

## Purpose

`mona_dsp.c` implements Mona-specific DSP boot, dual ASIC loading, 48/96 kHz ASIC switching, GML sample-rate and clock control, and digital-mode handling.

## Important APIs, Types, and Functions

`init_hw()` validates Mona, selects 56301 or 56361 DSP firmware, enables internal/S/PDIF/word/ADAT clocks, and sets RCA/optical/ADAT modes. `load_asic()` loads the PCI-card 48 kHz ASIC and external ASIC, checks status, and initializes the control register. `switch_asic()` chooses 48 or 96 kHz PCI-card ASIC based on double-speed needs. `set_sample_rate()` swaps ASICs if needed, rejects ADAT double-speed, and maps fixed GML rates. `set_input_clock()` handles internal, S/PDIF, word, and ADAT and may switch ASICs using detected S/PDIF/word 96 kHz bits. `dsp_set_digital_mode()` handles RCA, optical, and ADAT with incompatible-clock fallback.

## Control Flow

Probe loads DSP plus both required ASIC stages. Rate changes under internal clock may temporarily drop `chip->lock` while loading a new ASIC, then relock to finish control-register writes. External clock changes similarly switch ASIC based on detected clock speed. Digital-mode changes force internal 48 kHz when needed and ensure ADAT does not use a 96 kHz ASIC.

## State and Persistence Behavior

Persistent fields include `asic_code`, `input_clock`, `digital_mode`, `digital_in_automute`, and `sample_rate`; comm-page state includes GML control bits and clock detect status. The selected ASIC image is part of runtime state and must match rate/mode.

## Dependencies and Integration Points

It depends on `echoaudio_gml.c`, shared DSP/ASIC loading, Mona firmware entries, and ALSA controls for rate, clock, and digital mode.

## Risks and Test Signals

Risks are lock ordering around sleeping ASIC loads, using the wrong ASIC for detected 96 kHz external clocks, and leaving ADAT in double-speed mode. Test with internal and external 44.1/48/88.2/96 kHz transitions, S/PDIF/word clock detection, ADAT mode switching, and monitor/gain persistence.

# sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/interface.h

## Purpose
This header models the memory-mapped Apple I2S interface registers and defines bit encodings used by the PCM driver to configure clocks, serial format, word sizes, interrupt causes, and codec message registers.

## Important APIs, Types, And Functions
`struct i2s_interface_regs` gives packed offsets for `intr_ctl`, `serial_format`, codec message registers, `frame_count`, `frame_match`, `data_word_sizes`, and peak-level registers. Clock-source constants describe 18.432 MHz, 45.1584 MHz, and 49.152 MHz roots. `i2s_sf_mclkdiv()` and `i2s_sf_sclkdiv()` encode supported divisors into the serial-format register while rejecting odd or reserved encodings. Word-size macros encode 16-bit and 24-bit input/output data plus channel counts.

## Control Flow
The inline divisor helpers are used during PCM prepare. Callers pass desired integer divisors and an output register accumulator; the helpers set the relevant bits on success and return `-1` for unsupported hardware encodings. The rest of the file is declarative register layout.

## State And Persistence
No software state is stored here. The definitions map persistent hardware state: interrupt pending/enable bits, current serial clocking, frame counter, and transfer word-size setup. The PCM driver writes `serial_format` and `data_word_sizes` only during prepare/reconfiguration.

## Dependencies And Integration Points
This header is consumed by `i2sbus.h` and `pcm.c`, and indirectly by `core.c` for resource-size validation of the I2S MMIO block. The register encodings are the hardware contract between ALSA PCM runtime choices and the Apple I2S cell.

## Risks And Test Signals
The macro `I2S_SF_EXT_SAMPLE_FREQ_INT_MASK` references `I2S_SF_SAMPLE_FREQ_INT_SHIFT`, which is not defined in this file; it appears unused but would fail if used. Divisor rejection must match hardware behavior, especially reserved encodings for divisors 1/3/5/14 and 1/3. Test signals include successful preparation across supported rates, correct 32x/64x bus-factor setup, and frame-count based pointers that advance monotonically under playback/capture.

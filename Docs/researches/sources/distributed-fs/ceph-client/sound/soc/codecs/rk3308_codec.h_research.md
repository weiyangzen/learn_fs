# sources/distributed-fs/ceph-client/sound/soc/codecs/rk3308_codec.h

## Purpose
This header defines the RK3308 internal codec register map and bitfields used by `rk3308_codec.c`. It covers global control, four ADC digital register groups, ALC registers, DAC digital registers, four ADC analog register groups, and DAC analog registers.

## Important APIs, types, and functions
There are no functions or exported types. Register macros such as `RK3308_ADC_DIG_CON01(ch)`, `RK3308_ADC_ANA_CON00(ch)`, and `RK3308_DAC_ANA_CON13` encode the grouped register layout. Bit macros define I2S modes, sample widths, master/slave bits, work bits, HPF settings, BIST paths, version-C digital gains, microphone enable/work/unmute bits, micbias level range, DAC headphone/lineout gains, HPMIX selects, and pop-sound values.

## Control flow and integration
The `.c` file composes these macros inside DAI format programming, hw_params, DAPM widgets/routes, reset, initialization, and bias-level power sequencing. Grouped ADC address macros are essential because capture channels are configured in left/right pairs across four groups.

## State and persistence
This file describes persistent hardware register state but does not maintain software state. Some definitions encode reset-value caveats: version-C ADC/DAC digital gain reset values are undocumented and corrected during initialization; HPMIX reset gain `0` is illegal and must be updated.

## Dependencies
The header relies on `BIT()` and other kernel bit macros being available via includes in users. It is tightly coupled to RK3308/RK3308BS TRM register semantics.

## Risks and test signals
Several comments distinguish version-specific behavior and unsupported hardware capabilities; incorrect macro reuse across chip versions could produce silent audio or bad clocks. The grouped macros mask channel index to two bits, so callers must validate group counts. Tests should verify every macro used in DAPM corresponds to the intended physical ADC/DAC channel, and that version-C gain defaults program the documented 0 dB values.

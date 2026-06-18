# sources/distributed-fs/ceph-client/drivers/staging/iio/frequency/dds.h

## Purpose
Defines IIO sysfs attribute helper macros for DDS output devices.

## Important APIs and Integration
Macros create consistently named `IIO_DEVICE_ATTR` or `IIO_CONST_ATTR` entries for output frequency, frequency scale, frequency symbol, phase, phase scale, phase symbol, pin-control enable, pin-controlled frequency/phase enable, output enable, per-output enable, waveform type, and waveform-type availability.

## State and Dependencies
The header stores no state and depends on IIO sysfs macro definitions supplied by including C files. It standardizes older custom sysfs naming used by AD9832 and AD9834 staging drivers.

## Risks and Test Signals
Risks are name-generation compatibility and macro misuse causing mismatched attribute names. Compile tests for both DDS drivers and sysfs inspection after probe are the main signals.

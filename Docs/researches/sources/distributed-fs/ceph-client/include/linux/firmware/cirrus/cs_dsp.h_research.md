# sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp.h` declares the Cirrus Logic DSP firmware support API for ADSP1/ADSP2/Halo cores, including DSP memory regions, coefficient controls, lifecycle management, raw data access, write sequences, and packed DSP chunk helpers. The source was read as a complete 360-line file for this report.

## Important APIs, Types, and Functions

Important definitions include region masks, 24-bit DSP word constants, acked-control timeout limits, write-sequence opcodes, `struct cs_dsp_region`, `struct cs_dsp_alg_region`, `struct cs_dsp_coeff_ctl`, `struct cs_dsp`, `struct cs_dsp_client_ops`, init/power/run/stop/remove APIs, clock/bus-error/watchdog APIs, debugfs APIs, coefficient read/write APIs, raw data read/write APIs, algorithm lookup, `struct cs_dsp_wseq`, write-sequence APIs, `struct cs_dsp_chunk`, chunk inline helpers, chunk read/write/flush APIs, and `cs_dsp_hibernate`.

## Control Flow

Client drivers initialize a `cs_dsp`, load WMFW and coefficient firmware through power-up APIs, create coefficient controls, run the core with pre/post client callbacks under `pwr_lock`, access controls and DSP memory, and stop/power down/remove the DSP. Write sequences record register operations for DSP-controlled replay. Chunk helpers pack/unpack non-byte-aligned DSP words.

## State and Persistence Behavior

`struct cs_dsp` stores device/regmap pointers, firmware identity, memory map, algorithm regions, boot/running/hibernating flags, control list, power lock, region locking, and debugfs filenames. Coefficient controls cache values and enabled/set flags. Persistence beyond runtime is firmware/device-specific.

## Dependencies and Integration Points

It depends on bits, device model, firmware loader, lists, and regmap. It integrates with audio codec/amplifier drivers, WMFW format definitions, coefficient binary loading, debugfs, regmap-backed hardware access, and client lifecycle callbacks.

## Risks and Edge Cases

Control callbacks run under `pwr_lock`, so callbacks must avoid deadlocks. DSP word packing is 24-bit and easy to mis-size. Acked controls have polling/timeout behavior. Firmware/control ABI drift can break coefficient parsing or raw memory access.

## Test Signals

Cirrus DSP KUnit tests, WMFW/bin parsing tests, coefficient read/write/acked-control timeout tests, power-up/down/run/stop sequencing tests, regmap fault injection, chunk pack/unpack tests, and debugfs lifecycle tests.

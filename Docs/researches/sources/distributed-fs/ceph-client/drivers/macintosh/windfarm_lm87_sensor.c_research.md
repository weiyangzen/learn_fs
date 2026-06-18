# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_lm87_sensor.c

## Purpose
Exposes the LM87 internal temperature sensor as a Windfarm sensor for Xserve G5 (`RackMac3,1`) systems, primarily for DIMM and processor-area thermal loops.

## Important APIs, Types, And Functions
`struct wf_lm87_sensor` wraps an I2C client and `wf_sensor`. `wf_lm87_read_reg()` performs register select and byte read with up to ten retries. `wf_lm87_get()` reads `LM87_INT_TEMP` (`0x27`) and returns the integer Celsius value shifted to 16.16 fixed point. `wf_lm87_probe()` scans child nodes named `int-temp`, looks at their `location`, and maps DIMM-related locations to `dimms-temp` and processor-related locations to `between-cpus-temp`.

## Control Flow
Module init refuses non-`RackMac3,1` machines, then registers an I2C driver for `"MAC,lm87cimt"` or OF compatible `"lm87cimt"`. Probe registers only recognized child-location combinations. Remove nulls the client pointer and unregisters the sensor.

## State, Dependencies, And Integration
The driver depends on I2C master send/receive, OF child-node traversal, and Windfarm sensor APIs. RM31 consumes `dimms-temp` to clamp CPU fan output and backside fan minimum; other Xserve loops may use the between-CPU sensor name if present.

## Risks And Test Signals
Only the internal LM87 temperature is exposed, despite the chip supporting more sensors. The retry loop handles transient bus errors but prints a hard error after repeated failures. Recognition depends on location substrings. Test signals include machine-compatible gating, child-node parsing, retry/error behavior, fixed-point conversion, and unregister races returning `-ENODEV`.

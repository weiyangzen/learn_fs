# sources/distributed-fs/ceph-client/drivers/gnss/Makefile

## Purpose
This Makefile maps GNSS Kconfig symbols to core and driver objects.

## Important Entries
`gnss-y := core.o` builds the core. `gnss-serial-y := serial.o`, `gnss-mtk-y := mtk.o`, `gnss-sirf-y := sirf.o`, `gnss-ubx-y := ubx.o`, and `gnss-usb-y := usb.o` build the helper and concrete modules.

## Control Flow and State
There is no runtime state. Kbuild selects objects based on configuration.

## Dependencies and Integration Points
The build outputs correspond to the exported symbols in core and serial helper code.

## Risks and Test Signals
Build tests should verify that serial helper symbols resolve for MTK and UBX and that SiRF has no unnecessary dependency on `gnss-serial.o`.

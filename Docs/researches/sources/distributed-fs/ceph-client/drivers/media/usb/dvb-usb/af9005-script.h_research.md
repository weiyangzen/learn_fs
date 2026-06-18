# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/af9005-script.h

Purpose: contains the AF9005 OFDM initialization script used by `af9005_fe_init()`. The file documents that it was generated from bytes extracted from the Windows driver and converted by `createinit.py`.

Important APIs, types, and data: `RegDesc` describes one register-bit write with `reg`, `pos`, `len`, and `val`. `static RegDesc script[]` is a linear sequence of AF9005 register field writes. The array programs ADC/frequency-control values, AGC thresholds, DCA/FEQ/FEC-related settings, MPEG/OFSM control bits, and other hardware parameters. It is not exported as an API; inclusion into `af9005-fe.c` makes the static array local to that translation unit.

Control flow: `af9005_fe_init()` computes `scriptlen = sizeof(script) / sizeof(RegDesc)` and applies each entry with `af9005_write_register_bits()`. During that loop it also observes selected script entries to save original FCW bytes and unplug thresholds into `struct af9005_fe_state`. Those saved values are later restored during `af9005_fe_set_frontend()` before each tune.

State and persistence: the script itself is static read-only driver data after module load. Its effects persist in AF9005 hardware registers until later register writes, retune, reset, or disconnect. Some script values become software baseline state because `af9005-fe.c` copies them into `original_fcw` and threshold fields.

Dependencies and integration points: depends on Linux integer typedefs being available through the including C file. It uses raw register addresses rather than the symbolic names from `af9005.h` for many entries, though some addresses correspond to named AF9005 register fields. Its only direct consumer is `af9005-fe.c`.

Risks: generated magic values are hard to audit and have no semantic grouping. Because `RegDesc` and `script` are defined in a header, including it from multiple C files would create multiple static copies and type definitions. Register field length/position mistakes are only visible on hardware. Changing script order can alter hardware bring-up behavior.

Test signals: AF9005 hardware init is the primary test. Useful checks include comparing USB/register traces against a known-good driver, verifying that all script entries return success, validating saved FCW/threshold values, and confirming tune/lock behavior across supported bandwidths and tuner variants after script application.

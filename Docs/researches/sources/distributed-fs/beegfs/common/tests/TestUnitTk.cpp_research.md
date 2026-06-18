# sources/distributed-fs/beegfs/common/tests/TestUnitTk.cpp

Purpose: This test locks down binary unit conversion behavior in `UnitTk`.

Important APIs/types/functions: It covers `gibibyteToByte`, `mebibyteToByte`, `kibibyteToByte`, `byteToXbyte`, and `xbyteToByte`. Expected values use powers of two: KiB = 1024, MiB = 1048576, GiB = 1073741824.

Control flow: The first three tests convert representative doubles, including fractional `10.598`, to integer bytes and compare exact truncation/rounding results. `byteToXbyte` checks automatic unit choice and the optional display rounding flag. `xbyteToByte` validates reverse conversion for KiB, MiB, and GiB.

State and persistence behavior: No persistence is involved. The output affects config parsing and human-readable capacity display, which can influence operational decisions.

Dependencies and integration: `UnitTk::strHumanToInt64()` is used by metadata config parsing for buffer sizes, chunk sizes, and persistent file-event queue size. These tests indirectly protect that convention by pinning lower-level conversion math.

Risks and test signals: Signal is good for binary units and representative fractions. It does not cover invalid unit strings, decimal SI units, negative values, overflow, very small fractions, or full human-string parsing.

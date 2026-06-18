# sources/distributed-fs/ceph-client/drivers/misc/eeprom/Makefile

Purpose: maps EEPROM Kconfig options to object files in `drivers/misc/eeprom`.

Important APIs, types, and functions: object mappings include `at24.o`, `at25.o`, `max6875.o`, `eeprom_93cx6.o`, `eeprom_93xx46.o`, `digsy_mtc_eeprom.o`, `idt_89hpesx.o`, `ee1004.o`, and `m24lr.o`.

Control flow: no runtime control flow; Kbuild compiles objects according to selected config symbols.

State and persistence: no runtime state; controls build products only.

Dependencies and integration points: paired with the EEPROM Kconfig menu and source files in the same directory. External drivers may link against exported symbols from `eeprom_93cx6.o`.

Risks: Kconfig/Makefile drift would make options ineffective or compile unexpected code. Because some objects are helper libraries and some are bus drivers, link coverage matters for both built-in and module combinations.

Test signals: `make drivers/misc/eeprom/` with relevant config permutations, especially `EEPROM_93CX6=m/y` for exported symbols and AT24/AT25/EE1004 module builds.

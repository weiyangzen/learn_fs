# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acutils.h

## Purpose
Collects prototypes, callback types, constants, and small macros for ACPICA subsystem-wide utilities: strings, checksums, object conversion, reference counting, debugging, evaluation helpers, locks, caches, resources, owner IDs, UUIDs, address ranges, and diagnostic output.

## Important APIs, Types, And Functions
The header declares AML/resource size globals, decode string tables for debug/disassembler output, message redirection/prefix macros, `acpi_walk_aml_callback`, `acpi_pkg_callback`, and `struct acpi_pkg_info`. Utility families include ASCII/name validation, checksum verification, non-ANSI string helpers, string-to-integer conversion, global name/type formatting, subsystem init/shutdown, internal/external object copying, object reference management, trace/debug buffer dump, object deletion, `_STA`/power/HID/UID/CID/CLS evaluation, reader/writer locks, object creation, `_OSI` interface management, predefined method lookup/display, generic state allocation, integer math helpers, package tree walking, owner ID allocation, AML resource walking/validation, safe string functions, mutexes, memory caches/buffer initialization, allocation tracking, address range tracking, prefixed/predefined error output, predefined-name/device-ID/UUID matching, and UUID conversion.

## Control Flow, State, And Persistence
Most functions are implemented in `ut*` modules and operate on global ACPICA state: caches, mutexes, supported `_OSI` interfaces, owner ID bitmaps, address range lists, debug settings, and allocation ledgers. Object copy/delete/reference functions control operand-object lifetime and package traversal. Resource walkers iterate AML descriptors with callbacks. Error helpers centralize warning formatting and source-location suffixes.

## Dependencies And Integration Points
This is a high-fanout internal header included by nearly every ACPICA subsystem. It integrates with namespace evaluation, interpreter execution, debugger/disassembler output, resource manager, table manager, compiler/help tools, OS services, and optional allocation tracking. `ACPI_ASL_COMPILER`, `ACPI_APPLICATION`, `ACPI_DEBUG_OUTPUT`, `ACPI_DEBUGGER`, and related build flags expose different subsets.

## Risks And Test Signals
Because this is a prototype hub, signature or macro changes can break many modules. Behavioral risks include reference count imbalance, unsafe object copies, bad string-to-integer conversion, stale `_OSI` interface state, checksum false positives/negatives, and address range warning regressions. Test signals include ACPICA unit tests, kernel boot logs, namespace/device ID evaluation, AML resource validation, debug output formatting, allocation tracking runs, and compiler/disassembler builds.

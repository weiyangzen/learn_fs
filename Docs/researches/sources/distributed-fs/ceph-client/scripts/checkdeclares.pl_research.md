# sources/distributed-fs/ceph-client/scripts/checkdeclares.pl

## Purpose
`checkdeclares.pl` scans header files for duplicate forward `struct name;` declarations.

## APIs, Types, And Functions
It uses Perl strict mode, a `usage()` helper, per-file `%declaredstructs` counts, and a regex matching lines that contain only a struct forward declaration.

## Control Flow
The script requires at least one filename, opens each file, counts matching struct declarations, then prints a warning for any struct declared more than once. If no duplicates are found, it prints a clean summary.

## State And Persistence
State is in-memory counts per file and a total duplicate counter. It does not modify files.

## Dependencies And Integration Points
It depends on Perl and simple header formatting. It integrates with manual cleanup checks and complements include duplication scripts.

## Risks And Test Signals
Risks include ignoring macro/ifdef context and missing declarations with attributes or comments. Test signals are warnings for duplicated `struct foo;` lines and clean output for unique declarations.

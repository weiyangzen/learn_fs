# sources/distributed-fs/orangefs/src/io/description/dist-varstrip-parser.h

## Purpose
Declares the varstrip parser descriptor type and parser/free functions.

## Important APIs, Types, And Functions
Defines `struct PINT_dist_strips_s` with `server_nr`, `offset`, and `size`; typedefs `PINT_dist_strips`; declares `PINT_dist_strips_parse` and `PINT_dist_strips_free_mem`.

## Control Flow
Consumers parse a string into a dynamically allocated descriptor array and free it after mapping calculations.

## State And Persistence
The header defines no state. Parsed arrays are caller-managed heap memory.

## Dependencies And Integration Points
Includes `pvfs2-internal.h` and `pvfs2-types.h`; consumed by `dist-varstrip.c`.

## Risks And Test Signals
Risks are declaration drift and lack of ownership comments beyond function names. Parser unit tests and compile coverage are useful.

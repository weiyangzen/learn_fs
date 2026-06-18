<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/module.mk.in -->
# sources/distributed-fs/orangefs/src/proto/module.mk.in

## Purpose
Build-system fragment that adds the protocol encoding implementation files to the relevant OrangeFS build variables.

## Important APIs, Types, and Functions
No C APIs are defined. The fragment sets `DIR := src/proto`, appends `PINT-reqproto-encode.c` and `PINT-le-bytefield.c` to both `LIBSRC` and `SERVERSRC`, and appends `endecode-funcs.h` plus `endecode-funcs.c` to `LIBBMISRC`.

## Control Flow
When included by the parent make system, this fragment ensures the request protocol dispatcher and little-endian bytefield module are built into library and server targets, while primitive encode/decode wrappers are included in BMI-related library sources.

## State and Persistence
No runtime state. Build variables persist within the make evaluation context.

## Dependencies and Integration Points
Integrates the `src/proto` encoder files with the broader OrangeFS make/autoconf build. Source inclusion here must match headers and symbols referenced by client, server, and BMI components.

## Risks
Missing a source from the correct variable can produce link failures only in specific build targets. Adding a new encoder module requires updating this fragment and likely the dispatcher table. Listing a header in `LIBBMISRC` may rely on existing build rules tolerating header entries.

## Test Signals
Run full library, server, and BMI builds; inspect link lines for `PINT-reqproto-encode.o`, `PINT-le-bytefield.o`, and `endecode-funcs.o`; and test clean rebuilds after touching the listed files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/proto/module.mk.in -->

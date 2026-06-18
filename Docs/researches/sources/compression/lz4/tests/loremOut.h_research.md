# sources/compression/lz4/tests/loremOut.h

## Purpose
`loremOut.h` declares the stdout-oriented lorem ipsum generator used by the data generator CLI.

## Important APIs, Types, and Functions
The single public API is `LOREM_genOut(unsigned long long size, unsigned seed)`, documented as generating `size` bytes of compressible lorem ipsum text to stdout.

## Control Flow, State, and Persistence
The header has no state, no inline logic, and no includes. Runtime behavior is entirely implemented in `loremOut.c`.

## Dependencies and Integration Points
It is included by `datagencli.c` and implemented by `loremOut.c`. It pairs with `lorem.h`/`lorem.c` buffer generation but exposes only the streaming output form.

## Risks and Test Signals
The public contract is very small, so risk is limited to declaration drift or missing include guards if included repeatedly in unusual translation units. The expected signal is successful link resolution for `LOREM_genOut()` in the datagen CLI.

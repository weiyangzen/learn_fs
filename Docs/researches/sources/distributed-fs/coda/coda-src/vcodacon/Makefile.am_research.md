# sources/distributed-fs/coda/coda-src/vcodacon/Makefile.am

## Purpose
Builds the optional FLTK-based `vcodacon` GUI when both `BUILD_VCODACON` and `BUILD_CLIENT` are enabled.

## Important APIs, Types, And Functions
`bin_PROGRAMS = vcodacon` is conditional. Static sources are `Inet.cc`, `Inet.h`, `monitor.cc`, `monitor.h`, `util.cc`, and `util.h`. Generated sources are `vcodacon.cc` and `vcodacon.h` from `vcodacon.fl` via `$(FLUID)`. `LDADD` links base library and FLTK libraries.

## Control Flow
Automake builds generated FLUID sources first, compiles the GUI/network/monitor utilities, and links the FLTK executable. `CLEANFILES` removes generated sources.

## State And Persistence
No runtime state is defined here. Build state includes generated GUI source files.

## Dependencies And Integration Points
Depends on FLTK flags/libs, `lib-src/base`, and the FLUID interface compiler. Integrates generated UI widgets with handwritten monitor/network code.

## Risks
Missing FLUID or mismatched FLTK flags breaks builds. Generated sources are nodist, so source tarballs must include `vcodacon.fl` and regenerate. Conditional nesting can hide build rot unless enabled regularly.

## Test Signals
Configure with and without `BUILD_VCODACON`/`BUILD_CLIENT`, run FLUID generation, link against FLTK, clean/rebuild, and launch the GUI against a mariner socket.

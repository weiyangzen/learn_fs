# sources/distributed-fs/openafs/src/bubasics/Makefile.in

This makefile builds `libbubasics.a` and generated backup/tape interface headers and sources. It is the build bridge from `.xg` Rx definitions and `.et` error tables to installed backup headers used by bucoord, butc, and tape modules.

Important targets include `generated`, `libbubasics.a`, generated `butc`, `bumon`, `butm`, `tcdata`, and `butx` headers/sources, plus install/dest/clean. RXGEN produces client/server/XDR/header code for `butc.xg` and `bumon.xg`; COMPILE_ET produces error C and headers; `tcdata.h` is generated from `butc_errs.et`, `tcdata.p.h`, and `butm.h`.

State is build-output state: generated C/header files, objects, archive library, installed headers, and component version source. Dependencies are top-level OpenAFS make config, LWP config, RXGEN, COMPILE_ET, archiver/ranlib, and source `.xg`/`.et`/`.p.h` files.

Risks include generated-header ordering, consumers depending on installed include names rather than private `.p.h` files, stale generated artifacts, and clean removing generated files required before regen. Test signals are deterministic regeneration, archive contents, installed headers matching generated outputs, and downstream bucoord/butc build success.

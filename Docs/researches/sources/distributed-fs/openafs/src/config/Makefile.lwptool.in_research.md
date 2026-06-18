# sources/distributed-fs/openafs/src/config/Makefile.lwptool.in

Purpose: make fragment for libraries that need both LWP static objects and pthread/libtool objects from one source list.

Important APIs/types/functions: defines `.lo` suffix/pattern rules that call `$(LTLWP_CCRULE)`.

Control flow: included by hybrid modules; `lwptool` compiles a hidden `.lwp/*.o` copy and a libtool `.lo` copy for the same source.

State and persistence: creates `.lo` files plus mirrored `.lwp/*.o` files used later for static LWP libraries.

Dependencies and integration: depends on `LTLWP_CCRULE` and the `lwptool` script configured in `Makefile.config`.

Risks and test signals: risks include stale `.lwp` mirrors, filename assumptions during `.lo` to `.o` conversion, and missing libtool. Hybrid library builds and archives containing the `.lwp` objects are the relevant signals.

# sources/distributed-fs/coda/coda-src/asr/ruletypes.h

Purpose: Declares the C++ object model used by the ASR resolver grammar and runtime.

Important APIs/types: Classes `objname_t`, `depname_t`, `arg_t`, `command_t`, and `rule_t`; constants `NOREPLICAID` and `ALLREPLICAS`; exported `expandstring`.

Control flow and state model: `rule_t` owns object, dependency, and command lists plus match-time conflict metadata. `command_t` owns argument objects, and `arg_t` tracks replica selectors. Methods expose matching, expansion, execution, and printing.

Persistence and integration: No direct persistence. Integrates parser actions with resolver execution and Coda repair ioctls implemented in `ruletypes.cc`.

Risks and test signals: The header exposes fixed-size path/name arrays and manual ownership. Replica slots are sized by `VSG_MEMBERS`, while `ALLREPLICAS` is a sentinel value outside normal replica IDs.

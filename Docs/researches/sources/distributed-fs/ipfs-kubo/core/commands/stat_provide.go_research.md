# sources/distributed-fs/ipfs-kubo/core/commands/stat_provide.go

Purpose: deprecated compatibility shim for `ipfs stats provide`.

Important APIs/types/functions: `statProvideCmd` copies arguments, options, run function, encoders, and type from `provideStatCmd`.

Control flow: command execution is entirely delegated to `provideStatCmd`; only help/status differ.

State and persistence behavior: same as `provideStatCmd`, expected to be read-only provider statistics. This file itself has no state behavior.

Dependencies and integration points: depends on the provide command implementation being in the same package and stable enough for direct field reuse.

Risks: wrapper can drift in help text only; behavioral drift is avoided by direct delegation. It remains deprecated, so scripts should migrate to `ipfs provide stat`.

Test signals: command-tree validation covers structural correctness; provider stats behavior is covered where `provideStatCmd` is tested.

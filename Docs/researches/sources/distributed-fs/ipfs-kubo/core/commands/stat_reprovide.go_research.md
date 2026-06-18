# sources/distributed-fs/ipfs-kubo/core/commands/stat_reprovide.go

Purpose: deprecated compatibility shim for `ipfs stats reprovide`.

Important APIs/types/functions: `statReprovideCmd` delegates arguments, options, run function, encoders, and type to `provideStatCmd`.

Control flow: identical runtime behavior to `provideStatCmd`; only deprecation status and help text differ.

State and persistence behavior: expected read-only provider/reprovider stats via delegated command. This file has no direct state mutation.

Dependencies and integration points: keeps old command path alive while provider stats live under `ipfs provide stat`.

Risks: users may misread it as a separate reprovide-only statistic; help text explains provider stats are consolidated. Future removal can break legacy scripts.

Test signals: command-tree validation verifies schema; detailed behavior follows `provideStatCmd` tests.

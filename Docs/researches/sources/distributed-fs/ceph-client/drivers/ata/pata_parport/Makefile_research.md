# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/Makefile

## Purpose
Maps `PATA_PARPORT*` Kconfig symbols to the core `pata_parport.o` object and each parallel-port IDE protocol object.

## Important APIs, Types, And Functions
The Makefile uses standard `obj-$(CONFIG_...) += file.o` entries for the core and all protocol modules: `aten`, `bpck`, `bpck6`, `comm`, `dstr`, `epat`, `epia`, `fit2`, `fit3`, `friq`, `frpw`, `kbic`, `ktti`, `on20`, and `on26`.

## Control Flow
Build control flow is declarative: enabled symbols add objects to the kernel or module build.

## State And Persistence
No runtime state. Build artifacts and module availability persist according to the kernel configuration.

## Dependencies And Integration Points
Directly consumes symbols from the adjacent Kconfig and emits modules that depend on the exported `pata_parport` protocol registration API.

## Risks And Edge Cases
Object names must stay aligned with Kconfig symbols and source files. Missing core selection would leave protocol modules without exported registration symbols.

## Test Signals
`make M=drivers/ata/pata_parport` with all options enabled, modular-only builds, built-in builds, and modpost symbol dependency checks.

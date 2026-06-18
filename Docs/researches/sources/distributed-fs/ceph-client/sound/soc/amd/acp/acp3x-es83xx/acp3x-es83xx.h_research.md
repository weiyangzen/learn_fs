# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp3x-es83xx/acp3x-es83xx.h

## Purpose
`acp3x-es83xx.h` declares the ES83xx machine-ops initializer used by ACP legacy machine data.

## Important APIs, Types, and Functions
The single exported declaration is `acp3x_es83xx_init_ops(struct acp_mach_ops *ops)`, which fills optional callbacks for probe, widget configuration, link configuration, suspend, and resume.

## Control Flow
Including code calls the initializer when it wants the generic ACP machine path to delegate ES83xx-specific behavior through `struct acp_mach_ops`.

## State and Persistence
The header owns no state. It depends on `struct acp_mach_ops` being visible from `acp-mach.h` before use.

## Dependencies and Integration Points
It is included by ES83xx-related machine selection code and implemented by `acp3x-es83xx.c`.

## Risks
The header does not include `acp-mach.h` itself, so include ordering matters. Prototype drift would break board-specific op installation at build time.

## Test Signals
Build coverage for ES83xx support and runtime confirmation that ES83xx callbacks are installed and invoked for `ESSX8336` systems.

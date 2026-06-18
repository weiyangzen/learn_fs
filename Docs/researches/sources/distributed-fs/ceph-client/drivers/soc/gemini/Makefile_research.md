
# sources/distributed-fs/ceph-client/drivers/soc/gemini/Makefile

## Purpose
Always builds the Gemini SoC initialization object in this directory.

## Important APIs, Types, and Functions
No runtime APIs. The rule is `obj-y += soc-gemini.o`.

## Control Flow
The object participates in built-in kernel linking whenever the directory is included by the parent build.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates with the Gemini SoC init code in `soc-gemini.c`.

## Risks
The object is unconditional at this directory level; runtime machine compatibility guard in the C file prevents action on non-Gemini systems.

## Test Signals
Build inclusion and no-op boot behavior on non-Gemini machines.

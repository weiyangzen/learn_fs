# sources/distributed-fs/coda/coda-src/egasr/Makefile.am

## Purpose
Automake rules for client-side easy graphical ASR/repair utilities.

## APIs, Types, and Functions
When `BUILD_CLIENT` is enabled, builds `filerepair` and `removeinc`, and distributes scripts `xfrepair` and `xaskuser`. `filerepair` links `libkerndep` and `libbase`; `removeinc` also links `libcodadir`.

## Control Flow, State, and Persistence
No runtime behavior. Build metadata wires repair programs to kernel-dependency pioctl support and directory helpers.

## Dependencies and Integration
Depends on base, kerndep, vicedep, dir, and vv include trees. It integrates these utilities into the client installation.

## Risks and Test Signals
Risks include client-only conditional coverage and script/runtime dependencies not represented in link checks. Test signals are successful client build and installed `filerepair`, `removeinc`, `xfrepair`, and `xaskuser`.

# sources/distributed-fs/openafs/src/procmgmt/procmgmt_softsig.h

## Purpose
Adapts OpenAFS `opr/softsig.h` soft-signal APIs to the Windows process-management signal implementation.

## Important APIs, Types, And Functions
When `AFS_NT40_ENV` is defined, maps `opr_softsig_Init()` to `pmgt_SignalInit()` and `opr_softsig_Register(sig, handler)` to `pmgt_SignalRegister(sig, handler)`, with declarations for both process-management functions.

## Control Flow
Consumers can include this header after `opr/softsig.h` and call the standard soft-signal names. On NT, macro substitution routes calls to procmgmt; on non-NT platforms the header has no effect.

## State And Persistence
No state is defined here. Runtime state is managed by `procmgmt_nt.c` signal tables.

## Dependencies And Integration Points
Bridges Unix-oriented soft-signal call sites to the NT process-management library without scattering conditional compilation across users.

## Risks And Test Signals
Risks are include-order dependency and signature drift between `opr_softsig` and `pmgt` handlers. Test signals are successful NT compilation of soft-signal consumers and runtime registration/delivery of handlers through procmgmt.

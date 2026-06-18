# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eq.h

## Purpose
Defines private data structures for the AU88x0 hardware equalizer implementation.

## Important APIs, Types, And Functions
`auxxEqCoeffSet_t` stores left/right coefficient arrays and left/right gain arrays. `eqhw_t` stores hardware filter count and a coefficient sign/polarity flag. `eqlzr_t` wraps hardware state, bypass gain fields, band count, bypass flag, A3D bypass factors, active coefficient set, and the 20-value left/right gain cache.

## Control Flow
This header has no executable flow. `au88x0_eq.c` initializes and mutates the fields while programming registers and serving ALSA control callbacks.

## State And Persistence
Instances live inside `vortex_t` and are reset by `vortex_Eqlzr_init()`. Settings are in-memory only and not persisted across reloads.

## Dependencies And Integration Points
Depends on kernel integer typedefs from including files. It is tightly coupled to the reverse-engineered field naming in `au88x0_eq.c`.

## Risks
Field names such as `this04`, `this28`, and `this54` reflect translated binary layouts and obscure semantics. The structure layout is not hardware ABI, but mistaken interpretation can lead to wrong register programming or user control behavior.

## Test Signals
Build coverage verifies all fields used by the EQ implementation. Runtime tests for EQ enable, band gain changes, and peak readings exercise the structure state transitions.

# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_xtalk.h

## Purpose
Declares XTALK constants, array typedefs, output mode IDs, and static function prototypes for the crosstalk hardware implementation.

## Important APIs, Types, And Functions
Defines `XTDLINE_SZ`, `XTGAINS_SZ`, `XTINST_SZ`, mode IDs `XT_HEADPHONE`, `XT_SPEAKER0`, `XT_SPEAKER1`, and `XT_DIAMOND`, and array types `xtalk_dline_t`, `xtalk_gains_t`, `xtalk_instate_t`, `xtalk_coefs_t`, and `xtalk_state_t`. It also declares static XTALK programming helpers consumed by the same compilation unit pattern.

## Control Flow
No executable flow. The prototypes let A3D code call XTALK helpers when implementation fragments are composed together.

## State And Persistence
Only type and constant definitions. Runtime state is held in the implementation and hardware registers.

## Dependencies And Integration Points
Includes `au88x0.h` for `vortex_t` and integer types. Used by `au88x0_xtalk.c` and `au88x0_a3d.c`.

## Risks
The header has duplicate `vortex_XtalkHw_ProgramPipe()` declarations. All declared functions are `static`, reflecting a nonstandard include/compilation model; if build organization changes, linkage would need cleanup.

## Test Signals
Build coverage confirms prototype consistency. Runtime signals are indirect through A3D/XTALK initialization and playback.

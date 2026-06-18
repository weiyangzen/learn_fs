# sources/distributed-fs/ceph-client/sound/soc/intel/common/sof-function-topology-lib.h

## Purpose
Declares the Intel SOF separated-function topology helper used by SoundWire-capable machine code.

## Important APIs, Types, And Functions
The header exposes `sof_sdw_get_tplg_files(struct snd_soc_card *card, const struct snd_soc_acpi_mach *mach, const char *prefix, const char ***tplg_files, bool best_effort)`. It includes only the declaration and include guard.

## Control Flow, State, And Persistence
The header has no state or control flow. It defines the ABI contract for callers that allocate or pass a topology filename array and decide whether unsupported links should be skipped.

## Dependencies And Integration Points
Consumers must already have ASoC and ACPI machine types visible through their includes. The implementation depends on firmware loading and card prelink traversal.

## Risks And Test Signals
Risks are declaration drift from the implementation and ambiguous ownership/capacity of `tplg_files`. Test signals are compile coverage for all users and runtime validation that callers size the returned filename array for the number of card prelinks.

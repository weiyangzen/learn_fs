# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_blit_shaders.h

## Purpose

`si_blit_shaders.h` provides the static SI default clear-context command stream used during command-processor startup. Despite the filename, this snapshot contains default register-state packets rather than shader program text: `si_default_state` is written into the GFX ring by `si_cp_start` between preamble begin/end commands so the CP has a known clear-state baseline.

## Important APIs, Types, and Data

- Include guard `SI_BLIT_SHADERS_H` prevents duplicate definitions.
- `static const u32 si_default_state[]` is an inline array of PM4 packet words and register values. It programs DB, PA_SC, VGT, CB, PA_CL, PA_SU, streamout, centroid, AA, and related context/config registers.
- `static const u32 si_default_size = ARRAY_SIZE(si_default_state)` exposes the dword count to `si.c` for ring-space reservation and iteration.

## Control Flow

The array is consumed in `si_cp_start`. After a first ring submission initializes ME and CE partition bases, CP is enabled, the ring is locked for `si_default_size + 10` dwords, `PACKET3_PREAMBLE_BEGIN_CLEAR_STATE` is emitted, every dword in `si_default_state` is copied to the ring, `PACKET3_PREAMBLE_END_CLEAR_STATE` is emitted, and a `PACKET3_CLEAR_STATE` command applies the baseline. Additional context registers for vertex reuse and output deallocation are then written explicitly.

## State and Persistence Behavior

This header is immutable data, but consuming it changes persistent GPU context state. Because the array is `static const` in a header, each translation unit that includes it gets an internal copy. In this subset, `si.c` includes it and uses the internal copy directly.

## Dependencies and Integration Points

- Requires `u32` and `ARRAY_SIZE` from the Radeon/Linux include context.
- The numeric packet words depend on SI PM4 packet encoding and register offsets from `sid.h`.
- Integrated only by `si.c` in this subset, specifically CP clear-state initialization.

## Risks and Edge Cases

- Raw numeric packet/register words are difficult to review; comments identify many registers but some entries have blank comments.
- `si_default_size` is a `u32` initialized from `ARRAY_SIZE`; any future growth beyond ring reservation assumptions would affect `si_cp_start`.
- Because the data is in a header, accidental inclusion by multiple C files increases object size and can create divergent local copies if modified under conditional compilation.
- Incorrect default state can cause rendering, compute, or clear-state failures that appear far from CP startup.

## Test Signals

- CP startup tests should verify `si_cp_start` reserves enough ring space, emits the full array, and successfully passes subsequent `PACKET3_CLEAR_STATE` and ring tests.
- GPU rendering smoke tests after resume/reset should catch invalid default DB/CB/PA/VGT state.
- Static checks can compare the array length and packet counts against expected PM4 packet payload sizes.

# File Research: sources/block-storage/linux-dm/drivers/md/dm-verity-fec.h

## Purpose
Defines dm-verity FEC constants, option names, configuration state, per-bio state, and enabled/disabled build interfaces.

## Main Interfaces
- FEC constants: RS parameters, buffer counts, recursion limit, and option-name strings.
- `struct dm_verity_fec` stores FEC device, bufio clients, RS layout, mempools, and buffer cache.
- `struct dm_verity_fec_io` stores per-bio Reed-Solomon state, erasures, buffers, output, and recursion depth.
- Enabled declarations cover FEC decode, status, per-IO init/finish, option parsing, constructor allocation, constructor validation, and destruction.
- Disabled stubs return false, `-EOPNOTSUPP`, `-EINVAL`, or no-op success as appropriate.

## Control Flow
There is no runtime control flow in the header. Compile-time `CONFIG_DM_VERITY_FEC` selects either the real API declarations and `DM_VERITY_OPTS_FEC == 8`, or stubs and `DM_VERITY_OPTS_FEC == 0`.

## State And Synchronization
The header defines state layout only. Runtime allocation, ownership, and synchronization are handled in `dm-verity-fec.c` and the parent dm-verity target.

## Integration Points
Included by `dm-verity-target.c` and `dm-verity-fec.c`. It includes `dm-verity.h` for parent types and Linux `rslib` for `struct rs_control`.

## Notable Behaviors
- `DM_VERITY_FEC_BUF_MAX` is derived from `PAGE_SHIFT` and the number of RS blocks per buffer.
- Disabled builds keep dm-verity optional-argument accounting consistent by setting FEC option count to zero.
- FEC option names are part of the dm-verity table ABI: `use_fec_from_device`, `fec_blocks`, `fec_start`, and `fec_roots`.

## Risks And Review Focus
- Per-bio data layout depends on `struct dm_verity_fec_io` being appended after dm-verity's variable-length fields.
- Changing constants affects memory pressure, correction capacity, and table ABI validation.

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_hwseq.h

## Purpose
`dcn32_hwseq.h` declares the DCN32 generation-specific hw sequencer entry points implemented in `dcn32_hwseq.c` and consumed by `dcn32_init.c` and derivative generations.

## Important APIs, types, and functions
The header exports power-gating controls, idle optimization, SubVP and phantom helpers, MCM color functions, init and bandwidth hooks, ODM/DSC programming, DCCG pixel divider helpers, link-output disable, and update-lock helpers. Types are intentionally forward-referenced through `hw_sequencer_private.h`, including `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dc_link`, `struct link_resource`, and `union block_sequence_params`.

## Control flow
This header has no runtime control flow. Its declarations define the compile-time contract used to populate public `hw_sequencer_funcs` and private `hwseq_private_funcs` tables.

## State and persistence behavior
The header owns no state. The declared functions mutate live DC hardware, DMUB state, pipe context fields, link PHY state, and DC capability/debug flags in the corresponding C implementation.

## Dependencies and integration points
It depends on `hw_sequencer_private.h` for callback table and core display types. It is included by DCN32 init code and by newer generations, such as DCN35/DCN351 init paths, that reuse DCN32 color, pixel-divider, link, or DSC status behavior.

## Risks and edge cases
The header declares `dcn32_cab_for_ss_control`, but the matching implementation is not present in the read source file, so any consumer would require a definition elsewhere or fail at link time. The broad declaration set also means signature drift affects multiple generations that reuse these helpers.

## Test signals
Build coverage is the primary test signal: DCN32 and derivative ASIC objects must compile and link. Runtime signals come indirectly from all vtable hooks that bind these declarations.

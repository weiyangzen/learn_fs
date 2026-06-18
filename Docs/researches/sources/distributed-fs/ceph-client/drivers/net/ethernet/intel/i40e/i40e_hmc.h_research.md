# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_hmc.h

## Purpose
`i40e_hmc.h` declares the shared HMC data model, constants, reference-count helpers, hardware register programming macros, address-range calculation macros, and low-level HMC allocation/removal APIs used by i40e HMC implementations.

## Important APIs, types, and functions
- HMC sizing constants include `I40E_HMC_PD_CNT_IN_SD`/`I40E_HMC_MAX_BP_COUNT` at 512 entries, direct backing pages at 2 MiB, paged backing pages at 4 KiB, and 4 KiB alignment.
- `struct i40e_hmc_obj_info` describes each HMC object class with FPM base, maximum count, requested count, and object size.
- `enum i40e_sd_entry_type` distinguishes invalid, paged, and direct segment descriptors.
- `struct i40e_hmc_bp`, `struct i40e_hmc_pd_entry`, `struct i40e_hmc_pd_table`, `struct i40e_hmc_sd_entry`, `struct i40e_hmc_sd_table`, and `struct i40e_hmc_info` define the in-memory HMC ownership tree.
- `I40E_SET_PF_SD_ENTRY`, `I40E_CLEAR_PF_SD_ENTRY`, and `I40E_INVALIDATE_PF_HMC_PD` program PFHMC registers for SD validity and PD cache invalidation.
- `I40E_FIND_SD_INDEX_LIMIT` and `I40E_FIND_PD_INDEX_LIMIT` translate object ranges into SD/PD index ranges.
- Function prototypes expose SD/PD add and removal helpers implemented in `i40e_hmc.c`.

## Control flow and behavior
The header establishes the contract used by LAN HMC creation. Higher layers configure `hmc_info->hmc_obj[type]` with an FPM base and object size. The index macros then compute the first and one-past-last SD or PD index touched by an object range. Add/remove functions use these indexes to allocate software entries and DMA backing pages. Register macros encode physical addresses, SD type, valid bits, BP count, and command bits into PFHMC registers using `wr32`.

## State and persistence
The structures persist for the lifetime of the initialized PF HMC, rooted at `struct i40e_hw::hmc`. State is entirely in kernel memory plus hardware HMC registers. Reference counts in SD, PD table, and backing-page objects are the primary lifetime state.

## Dependencies and integration points
This header includes allocation support, MMIO helpers, and register definitions. It depends on Linux `upper_32_bits`, `BIT`, and `BIT_ULL` helpers. Its structures are consumed by `i40e_hmc.c` and `i40e_lan_hmc.c`, and the register macros depend on PF-only hardware access semantics.

## Risks and edge cases
- The range macros assume nonzero `cnt`; if callers pass zero, `fpm_limit - 1` underflows.
- Reference-count macros perform unchecked arithmetic and are not atomic; callers must serialize HMC lifecycle operations.
- Register macros are statement-like blocks, not `do { } while (0)`, so they need careful use in control-flow contexts.
- SD/PD index calculations depend on object sizes/bases being initialized and aligned consistently with hardware expectations.

## Test signals
Compile coverage catches structure/prototype drift. Runtime signals include successful LAN HMC configure/shutdown, correct PFHMC register programming under direct and paged models, no invalid index debug logs from implementation files, and queue context set/clear operations resolving to valid DMA-backed HMC memory.

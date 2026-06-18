# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_processpptables.h

## Purpose
`vega20_processpptables.h` declares the Vega20 PPTable function table used by the hwmgr initializer.

## Important APIs, Types, and Functions
It includes `hwmgr.h` and exports `extern const struct pp_table_func vega20_pptable_funcs;`. The function table provides `.pptable_init` and `.pptable_fini` implemented in `vega20_processpptables.c`.

## Control Flow
No direct control flow exists. `vega20_hwmgr_init()` assigns `hwmgr->pptable_func = &vega20_pptable_funcs`, allowing generic PowerPlay lifecycle code to invoke the Vega20 PPTable parser.

## State and Persistence
No state is declared. The referenced function table manages `hwmgr->pptable` when invoked.

## Dependencies and Integration Points
It depends on the generic `struct pp_table_func` declaration from `hwmgr.h`. It is the compile-time link between the hwmgr backend and PPTable parser.

## Risks
The only material risk is declaration/definition mismatch or failing to include this header where `vega20_hwmgr_init()` assigns the function table.

## Test Signals
Build success and successful PowerPlay table initialization on Vega20 hardware validate this interface.

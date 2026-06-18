<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/config.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/config.h

Purpose: Defines the execution-state enum used by the configuration progress UI.

Important APIs/types: `STEP_STATE` values are `SS_STEP_TO_BE_DONE`, `SS_STEP_IN_PROGRESS`, `SS_STEP_FINISHED`, and `SS_STEP_FAILED`.

Control flow: No runtime logic. The enum values are consumed by `config_server_page.cpp` and `graphics.cpp` to track and render progress.

State and persistence: None.

Dependencies and integration points: Included by graphics and final configuration code.

Risks: Minimal; adding enum values requires updating `PaintStepGraphic`.

Test signals: Compile-time coverage and visual verification for each rendered step state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/config.h -->

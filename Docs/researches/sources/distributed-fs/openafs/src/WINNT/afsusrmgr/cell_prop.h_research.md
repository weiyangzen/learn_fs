# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/cell_prop.h

Purpose: declares the Account Manager cell property tab selector and entry point.

Important API/types: `CELLPROPTAB` provides `cptANY`, `cptPROBLEMS`, and `cptGENERAL`; `nCELLPROPTAB_MAX` documents the maximum tab count used for tab-index adjustment. `Cell_ShowProperties` opens or focuses the cell properties sheet, optionally selecting a target tab.

Control flow contract: callers pass `cptANY` for default selection or a specific tab. The implementation maps tab ids around optional/missing tabs.

State and persistence: none in the header; property changes are task-driven.

Dependencies/integration: depends on property sheet UI resources and global account-manager state in implementation.

Risks/test signals: tab index adjustment is fragile if tabs are added/removed without updating `nCELLPROPTAB_MAX`. Tests should cover all enum values against actual sheet composition.

# sources/distributed-fs/openafs/src/WINNT/afsapplib/test/resource.h

## Purpose
Defines resource IDs for the afsapplib wizard test program. It maps string resources, dialog templates, bitmap resources, button/control IDs, and App Studio next-value metadata used by `wiztest.cpp` and its resource script.

## Important APIs and Types
The file has no functions. Important constants include wizard button text and message strings (`IDS_NEXT`, `IDS_FINISH`, help/cancel IDs), dialog templates (`IDD_WIZARD`, `IDD_STEP1`, `IDD_STEP2`, `IDD_STEP3`), bitmap resources (`IDB_GRAPHIC_16`, `IDB_GRAPHIC_256`), navigation buttons (`IDNEXT`, `IDBACK`), radio controls (`IDC_GOTO_TWO`, `IDC_GOTO_THREE`), and pane controls (`IDC_WIZARD_LEFTPANE`, `IDC_WIZARD_RIGHTPANE`).

## State, Dependencies, and Integration
This is compile-time resource state shared with Windows `.rc` files and the wizard test source. Several IDs intentionally overlap across different resource classes, which is normal in Win32 resource tables but requires context-sensitive use.

## Risks and Test Signals
Changing IDs can break dialog procedure message handling and wizard template binding. The overlap between `IDD_STEP2` and `IDB_GRAPHIC_256`, and between `IDC_GOTO_THREE` and `IDC_WIZARD_LEFTPANE`, is acceptable only because they are used in different namespaces or templates. Test signals are successful resource compilation and manual wizard navigation through all three pages.

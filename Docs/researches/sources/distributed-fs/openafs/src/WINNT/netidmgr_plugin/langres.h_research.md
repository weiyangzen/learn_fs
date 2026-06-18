# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/langres.h

## Purpose
Central resource ID map for the core AFS NetIDMgr plugin.

## Important APIs, Types, And Functions
Defines IDs for plugin descriptions, dialogs, config panels, icons, method strings, tooltips, credential text, attribute descriptions, errors, help action strings, status tooltips, context menu commands, and dialog controls.

## Control Flow
No runtime control flow; C files call `LoadString()`, `LoadImage()`, and use dialog/control IDs based on this map.

## State And Persistence
Defines the stable numeric contract between compiled code and language/resource DLLs.

## Dependencies And Integration Points
Used by `afsplugin.c`, `afsnewcreds.c`, `main.c`, config/icon/help files, and resource compiler inputs.

## Risks
Duplicate IDs intentionally share values across different resource classes, which is normal for Windows resources but risky if copied into the wrong namespace. Any ID drift breaks UI loading or command dispatch.

## Test Signals
Resource compilation, plugin startup string/icon loads, dialog creation, tooltip text, method descriptions, help action labels, and menu command routing.

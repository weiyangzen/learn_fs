# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/help/afsplhlp.h

## Purpose
Defines HTML Help context IDs for the AFS NetIDMgr plugin UI.

## Important APIs, Types, And Functions
Maps controls/actions such as obtain, cell, realm, method, add/delete, token list, service status/start/stop/version/company/control panel, and start-afscreds to numeric IDs.

## Control Flow
No executable control flow. `afsnewcreds.c` and configuration dialogs use these IDs in help context arrays passed to `afs_html_help()`.

## State And Persistence
Static numeric resource contract only.

## Dependencies And Integration Points
Integrated with `.chm`/HTML Help topic maps and Win32 `WM_HELP` processing.

## Risks
IDs must stay synchronized with help content; otherwise context help opens wrong or missing topics.

## Test Signals
Press F1/help on each mapped UI control and verify expected popup/topic.

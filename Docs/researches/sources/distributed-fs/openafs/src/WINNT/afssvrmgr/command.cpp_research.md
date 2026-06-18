<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.cpp

## Purpose
Centralizes menu/context command dispatch for the server manager.

## Important APIs, Types, And Functions
`StartContextCommand` maps command IDs to dialogs, property sheets, view changes, or tasks. `Command_OnProperties` routes by object type. `Command_OnIconView` updates server/child list view mode.

## Control Flow
The dispatcher derives active tab and effective identity, ignores cell identities for most object commands, then switches through columns, refresh, sync/salvage, fileset, server, service, cell, credential, option, and help commands.

## State And Persistence
This file holds no state. Commands mutate global views, credentials/cell state, and server/fileset/service state through invoked modules/tasks.

## Dependencies And Integration Points
Includes many feature modules; called by menus/list subclasses. Depends on `StartTask`, `Server_GetDisplayedTab`, global `g.lpiCell`, and feature entry points.

## Risks And Edge Cases
Many invalid contexts silently no-op. Some null identities are valid for create/restore/global commands. New menu IDs require careful central switch updates.

## Test Signals
Command matrix over null/server/service/aggregate/fileset/cell contexts, properties routing, refresh, and view-mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/command.cpp -->

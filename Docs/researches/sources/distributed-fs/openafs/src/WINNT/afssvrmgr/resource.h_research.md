# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/resource.h

## Purpose
`resource.h` is the Visual C++ resource identifier catalog for the Server Manager application. It assigns stable numeric IDs to localized strings, controls, dialogs, menus, icons, accelerators, animations, and commands.

## Important APIs, Types, And Functions
There are no functions. String IDs cover tab titles, column labels, status text, action names, alert descriptions/remedies/buttons, error messages, command-help labels, option text, and fileset/server/service operation messages. Control IDs cover main window controls, property page controls, fileset create/delete/move/dump/restore widgets, help dialogs, credentials/options, host/address/security/salvage controls, and shared buttons. Dialog/resource IDs include `IDD_MAIN`, service/aggregate/fileset tabs, operation dialogs, help dialogs, options, clone/dump/restore dialogs, and menus. Command IDs include view, refresh, properties, server/service/fileset actions, help, options, export, subset, icon-view, and keyboard accelerators.

## Control Flow
No executable flow exists. Dialog templates, menus, accelerators, C++ switch statements, help maps, and string formatters all use these IDs to bind UI resources to logic.

## State And Persistence
No runtime state is stored. The numeric assignments are effectively persistent ABI within compiled resources and code.

## Dependencies And Integration Points
Every afssvrmgr UI module depends on this header. The files in this work item reference IDs for display labels, help maps, options controls, fileset operation dialogs, problem controls, and commands such as `M_COLUMNS`.

## Risks And Edge Cases
The file intentionally contains reused numeric IDs for controls in different dialogs, which is normal but can confuse cross-dialog handlers. Resource ID collisions within the same dialog or command range would break message routing. Hand-edited changes can desynchronize `.rc` templates, help maps, and code.

## Test Signals
Test compile/resource compilation, opening each dialog, menu command routing, accelerator routing, help context registration, localization string formatting, and UI automation that exercises IDs referenced by display, options, help, problems, and fileset operation modules.

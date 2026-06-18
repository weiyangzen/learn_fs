# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/options.h

## Purpose
`options.h` declares the entry point for opening Server Manager options.

## Important APIs, Types, And Functions
It exposes `void ShowOptionsDialog(void)`.

## Control Flow
No logic exists in the header. Menu handlers call `ShowOptionsDialog` to show the modal property sheet.

## State And Persistence
No state is declared. The implementation edits and persists global `gr` settings.

## Dependencies And Integration Points
The header integrates the menu command layer with the options dialog implementation.

## Risks And Test Signals
Risks are limited to declaration drift. Compile coverage and invoking the Options menu validate the header.

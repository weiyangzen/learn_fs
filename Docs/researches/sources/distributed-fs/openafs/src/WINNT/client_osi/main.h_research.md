## sources/distributed-fs/openafs/src/WINNT/client_osi/main.h

Purpose: Declares menu IDs, Win32 harness functions, and shared screen buffer for the OSI test application.

Important APIs/types: Defines `IDM_*` command IDs, prototypes for initialization/window procedures/about dialog, display helpers, `HW_NLINES`, and `main_screenText`.

Control flow/state: No logic; exposes global display state to test modules.

Dependencies/integration: Used by `main.c`, `basic.c`, and other test modules. Contains compatibility macros for horizontal scroll message extraction.

Risks/tests: Global `main_screenText[10][80]` invites truncation from `wsprintf`. Test all menu IDs against resources and display writes for overflow risk.

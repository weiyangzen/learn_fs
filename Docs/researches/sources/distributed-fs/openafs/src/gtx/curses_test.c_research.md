# sources/distributed-fs/openafs/src/gtx/curses_test.c

## Purpose
Simple standalone curses smoke test used to verify basic curses availability and behavior.

## Important APIs, Types, And Functions
The K&R-style `main` calls `initscr`, `scrollok`, `clear`, `addstr`, `refresh`, `box`, `standout`, `standend`, and `endwin`.

## Control Flow
The program initializes curses, enables scrolling, clears the screen, writes a normal string, refreshes, draws a box on the standard screen, writes a standout string, refreshes again, ends standout mode, and restores the terminal with `endwin`.

## State And Persistence
It temporarily mutates terminal/curses state and writes to the terminal only.

## Dependencies And Integration Points
Built by `gtx/Makefile.in` when tests are requested and depends on configured curses headers/libraries. It is independent of the higher-level gtx window abstraction.

## Risks And Test Signals
The test is manual and should be run in a real terminal; failure to call `endwin` after a crash can leave terminal modes altered. Signals are successful link, visible text/box output, standout mode rendering, and terminal restoration.

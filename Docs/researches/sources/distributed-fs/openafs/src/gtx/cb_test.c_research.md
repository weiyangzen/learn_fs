# sources/distributed-fs/openafs/src/gtx/cb_test.c

## Purpose
Manual test program for the gator text circular buffer package.

## Important APIs, Types, And Functions
The K&R-style `main` calls `gator_textcb_Init`, `gator_textcb_Create`, `gator_textcb_Write`, `gator_textcb_BlankLine`, and `gator_textcb_Delete`. It inspects `struct gator_textcb_hdr` and `struct gator_textcb_entry` fields directly.

## Control Flow
The program prompts for debug mode, creates a 100-entry buffer with 80 characters per entry, performs several writes including highlighted and bulk text, inserts blank lines, prints buffer metadata and entries, pauses for user input, writes many small entries to force wraparound, prints all entries again, then deletes the buffer and exits.

## State And Persistence
All state is heap memory owned by the circular buffer plus console input/output. No files are written.

## Dependencies And Integration Points
Linked by `gtx/Makefile.in` against the gtx library. It exercises the text circular buffer implementation used by text objects.

## Risks And Test Signals
It is interactive, uses `scanf` without robust input validation, and reaches into internal structures, so it is more diagnostic than automated. Useful signals are successful initialization, correct wraparound metadata, preserved highlight/inversion fields, clean deletion, and no crashes under repeated writes.

# sources/distributed-fs/openafs/src/gtx/textcb.c

Purpose: implements the circular fixed-line text buffer backing GTX text objects.

Important functions: `gator_textcb_Init`, `gator_textcb_Create`, internal `bumpEntry`, `gator_textcb_Write`, `gator_textcb_BlankLine`, and `gator_textcb_Delete`.

Control flow and state: create allocates one contiguous text buffer, an entry array, a header, and a blank-line template. `bumpEntry` advances current entry ID/index, clears the target entry, and advances oldest entry after wraparound. `gator_textcb_Write` write-locks the buffer, copies chunks into the current entry, records highlight inversions when highlight changes mid-line, wraps full lines, and optionally skips to a new entry. Blank lines bump entries; delete write-locks, frees buffer/entries/blank line/header.

Dependencies and integration: uses AFS locks and `gtxtextcb.h`; consumed by `textobject.c`.

Risks: `gator_textcb_BlankLine` mutates without taking the buffer lock; delete has no NULL guard; allocation size uses `int`; newline-specific line breaks described in comments are not actually handled specially. Test signals should cover wraparound, skip, blank lines, highlight inversions, deletion, NULL writes, and concurrent blank/write behavior.

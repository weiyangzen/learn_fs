# sources/distributed-fs/openafs/src/gtx/gtxtextcb.h

Purpose: declares the circular text buffer used by GTX text objects.

Important APIs and types: `GATOR_TEXTCB_MAXINVERSIONS`, `struct gator_textcb_entry` with monotonically assigned ID, base highlight, inversion positions, used character count, and text pointer; `struct gator_textcb_hdr` with lock, capacity, current/oldest entry ids and indexes, entry array, and blank-line buffer. Public operations are init, create, write, blank-line insertion, and delete.

Control flow and state: the buffer stores fixed-length lines and rotates when entries fill or callers request skips. Highlight inversions capture changes within a line, though display code currently uses only base line highlight.

Dependencies and integration: includes `afs/afs_lock.h`. `textobject.c` creates and writes through this API; tests indirectly exercise it through text objects.

Risks: callers must pass valid positive dimensions; delete assumes a non-NULL header. Highlight inversion capacity is fixed at 10. Test signals should include wraparound, line filling, skip behavior, blank lines, highlight transitions, and concurrent writer locking if used outside single-threaded input.

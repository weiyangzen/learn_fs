# sources/distributed-fs/openafs/src/gtx/gtxtextobj.h

Purpose: declares the GTX scrollable text object built on top of `gtxtextcb`.

Important APIs and types: `GATOR_OBJ_TEXT`, scroll direction constants, `struct gator_textobj` with lower-level rock, visible line count, circular buffer header, and first/last displayed entry IDs; `struct gator_textobj_params`; generic object operations; text-specific `gator_text_Scroll`, `gator_text_Write`, and `gator_text_BlankLine`; exported `gator_text_ops`.

Control flow and state: text object viewport state is represented by entry IDs rather than raw indexes, allowing it to follow circular buffer wraparound. Writes append to the circular buffer and can adjust displayed entry bounds.

Dependencies and integration: includes `gtxobjects.h` and `gtxtextcb.h`; instantiated by `objects.c`, displayed via generic `OOP_DISPLAY`, and exercised in object and frame tests.

Risks: destroy/release are no-ops in the implementation, so circular buffers are not reclaimed through object destruction. Display ignores per-line inversion arrays. Test signals should include creation, append, wrap, scroll up/down limits, blank lines, and memory cleanup expectations.

# sources/distributed-fs/openafs/src/gtx/textobject.c

Purpose: implements GTX scrollable text objects using `gator_textcb_hdr` circular buffers.

Important functions: exported `gator_text_ops`; `gator_text_create`, `gator_text_destroy`, `gator_text_display`, `gator_text_release`, `gator_text_Scroll`, `gator_text_Write`, and `gator_text_BlankLine`.

Control flow and state: creation allocates private `gator_textobj`, creates a circular buffer, stores visible line count from object height, and initializes first/last shown entry IDs. Display maps first shown entry ID to circular index, draws populated entries then blank lines through `WOP_DRAWSTRING`. Scroll clamps first/last shown IDs to buffer oldest/current. Write determines whether the current entry is visible before appending, then after buffer write adjusts viewport state when tracking the end. BlankLine delegates to the buffer and shifts viewport if it was at the end.

Dependencies and integration: includes text object, generic window, and backend headers; instantiated by `objects.c`; tested by `object_test` and `gtxtest`.

Risks: destroy/release are no-ops and leak circular buffers; write computes `writeDiff` before calling `gator_textcb_Write`, so viewport tracking may miss newly created lines; display ignores highlight inversions. Test signals should cover wrapping writes, visible-end tracking, scroll limits, blank-line follow behavior, and memory cleanup.

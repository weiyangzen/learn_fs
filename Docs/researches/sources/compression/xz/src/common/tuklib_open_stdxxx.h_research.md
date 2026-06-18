<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_open_stdxxx.h -->
# sources/compression/xz/src/common/tuklib_open_stdxxx.h

Purpose: declaration for `tuklib_open_stdxxx`.

Important APIs/types/functions: prefixed `tuklib_open_stdxxx(int err_status)`.

Control flow: declaration-only.

State and persistence: none in header.

Dependencies and integration: used by program startup code before normal file handling.

Risks: callers should invoke it early, before opening other files, or descriptor repair may not occupy 0/1/2.

Test signals: compile/link with implementation and test closed standard descriptors.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_open_stdxxx.h -->

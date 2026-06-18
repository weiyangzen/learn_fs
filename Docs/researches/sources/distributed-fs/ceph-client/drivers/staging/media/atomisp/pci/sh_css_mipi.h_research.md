# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mipi.h

Purpose: `sh_css_mipi.h` declares the local CSS MIPI buffer lifecycle helpers used by stream and pipeline setup code. It keeps MIPI initialization, allocation, free, and SP handoff behind a small interface.

Important APIs/types/functions: declarations are `mipi_init()`, `allocate_mipi_frames(struct ia_css_pipe *pipe, struct ia_css_stream_info *info)`, `free_mipi_frames(struct ia_css_pipe *pipe)`, and `send_mipi_frames(struct ia_css_pipe *pipe)`.

Control flow and state: the state is implemented in `sh_css_mipi.c` via per-port refcounts and global `my_css` frame/metadata arrays. Callers are expected to initialize once, allocate during stream setup, send before or during SP execution, and free during stream teardown.

Dependencies and integration: it includes CSS error/types/stream public headers for `ia_css_pipe`, `ia_css_stream_info`, and stream configuration types. It pairs with public `ia_css_mipi.h`, which provides frame size calculation declarations.

Risks: the header does not document ownership or valid modes, so misuse is easy: only buffered-sensor modes need buffers, online ISP2401 bypasses allocation, and NULL free has special "free all" semantics.

Test signals: lifecycle tests should call the declared functions in normal and teardown paths and validate no buffers remain in global state after free.

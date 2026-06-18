
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-format.c

## Purpose
Provides small shared CAMSS media-bus and pixel-format lookup helpers used by newer CAMSS components to avoid duplicating format search logic.

## Important APIs, Types, and Functions
Exports `camss_format_get_bpp()`, `camss_format_find_code()`, and `camss_format_find_format()`. They operate on arrays of `struct camss_format_info` declared in `camss-format.h`.

## Control Flow
`camss_format_get_bpp()` scans by media-bus code and returns `mbus_bpp`, warning and falling back to the first format if unknown. `camss_format_find_code()` either returns a requested code if present, returns the code at an enumeration index, returns zero for out-of-range enumeration, or falls back to the first supported code. `camss_format_find_format()` first searches exact bus-code plus fourcc, then falls back to bus-code-only, then returns `-EINVAL`.

## State and Persistence
The file is stateless. It reads caller-provided constant format tables and returns values only.

## Dependencies and Integration Points
Depends on Linux errno/bug helpers and `camss-format.h`. It integrates with VFE/CSID-style format tables and V4L2 pad/video format negotiation.

## Risks and Test Signals
Fallback-to-first behavior is convenient but can hide unsupported user requests; callers must validate negative indices where required. Test signals include exact format matches, bus-code fallback, enumeration out-of-range returning zero, unknown bpp warning, and no out-of-bounds access for empty or malformed tables.

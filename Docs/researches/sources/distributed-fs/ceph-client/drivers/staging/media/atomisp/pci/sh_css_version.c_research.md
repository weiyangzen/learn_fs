# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_version.c

## Purpose
Builds the reported AtomISP CSS plus firmware version string.

## Important APIs, Types, and Functions
`ia_css_get_version(char *version, int max_size)` selects `ISP2400_CSS_VERSION_STRING` or `ISP2401_CSS_VERSION_STRING` based on `IS_ISP2401`, appends `FW:` and `sh_css_get_fw_version()`, and returns `0` or `-EINVAL`.

## Control Flow
The function checks that the caller buffer can contain CSS version, firmware version, and separators, then uses `strscpy()` and `strcat()` to assemble the result.

## State and Persistence Behavior
No state is modified. It reads platform type and firmware-version state from other AtomISP components.

## Dependencies and Integration Points
Includes AtomISP Linux public headers, `ia_css_version.h`, generated `ia_css_version_data.h`, error definitions, and firmware version access.

## Risks
The size check must remain conservative because subsequent `strcat()` calls assume room. Version strings are compile-time/generated plus firmware-provided data.

## Test Signals
Queries on ISP2400 and ISP2401 should return the correct prefix, include firmware version text, terminate with `"; "`, and reject too-small buffers.

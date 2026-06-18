# sources/distributed-fs/ceph-client/include/linux/bcm47xx_nvram.h

## Purpose
Declares Broadcom BCM47xx NVRAM initialization and lookup helpers, with stubbed `-ENOTSUPP` behavior when support is disabled.

## Important APIs, types, and functions
- `bcm47xx_nvram_init_from_iomem()` and `bcm47xx_nvram_init_from_mem()` initialize NVRAM contents from mapped or physical memory ranges.
- `bcm47xx_nvram_getenv()` retrieves a named variable into a caller buffer.
- `bcm47xx_nvram_gpio_pin()` parses a named GPIO pin setting.
- `bcm47xx_nvram_get_contents()` returns a vmalloc-backed copy and `bcm47xx_nvram_release_contents()` releases it with `vfree()`.

## Control flow and state
Platform code initializes NVRAM early, then drivers query variables. When `CONFIG_BCM47XX_NVRAM` is unset, all lookup/init calls fail or return NULL and release is a no-op.

## State and persistence behavior
NVRAM is persistent board firmware data. The header exposes read-only access and copied content release; mutation is not declared here.

## Dependencies and integration points
Depends on errno, integer types, and vmalloc. Integrated by BCM47xx platform setup, wireless/ethernet GPIO configuration, SPROM fallback, and board detection.

## Risks
Callers must handle disabled support and missing keys. Buffer lengths for `getenv()` must include terminator space. Contents returned from `get_contents()` must be released only with the matching helper.

## Test signals
Test enabled and disabled config builds, lookup of present/missing variables, truncation behavior, GPIO parsing, init from memory bounds, and content-copy release.

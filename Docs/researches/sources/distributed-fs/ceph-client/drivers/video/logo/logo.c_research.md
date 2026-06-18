# sources/distributed-fs/ceph-client/drivers/video/logo/logo.c

Purpose: runtime selector for compiled-in Linux boot logos. It chooses the best enabled logo for a requested color depth unless logos have been disabled or already freed after init.

Important APIs, types, and functions: module parameter `nologo`, static `logos_freed`, `fb_logo_late_init`, and exported `fb_find_logo(int depth)`.

Control flow: `fb_logo_late_init` runs as a synchronous late initcall and marks initdata logo assets as freed. `fb_find_logo` returns `NULL` if `nologo` or `logos_freed` is true; otherwise it conditionally selects mono for depth >=1, VGA16 for depth >=4, and CLUT224 for depth >=8, with later checks overriding earlier ones.

State and persistence: `nologo` is a module parameter; `logos_freed` is runtime state protecting against use-after-initdata-free. Logo assets themselves are generated `__initconst` data and intentionally unavailable after late init.

Dependencies and integration points: depends on generated `linux_logo` objects declared by `linux/linux_logo.h`; exported to fbdev/console users. On M68K it includes setup headers.

Risks: callers after late init receive no logo. Selection is depth-based only, not display-specific. Module parameter permissions are zero, so runtime toggling through sysfs is not available.

Test signals: boot with and without `nologo`; build different logo configs; call `fb_find_logo` before and after late init; verify depth selection and no access after init data free.

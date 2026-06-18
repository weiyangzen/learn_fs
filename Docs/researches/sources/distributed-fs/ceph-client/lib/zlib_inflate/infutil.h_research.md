# sources/distributed-fs/ceph-client/lib/zlib_inflate/infutil.h

Purpose: Defines the inflate workspace wrapper and `WS(strm)` accessor used by the kernel static-allocation inflate implementation.

Important APIs/types:
- `struct inflate_workspace` contains `struct inflate_state inflate_state` and the backing `working_window`.
- With `CONFIG_ZLIB_DFLTCC`, it also includes `struct dfltcc_state` and over-allocates the window by one page for page alignment.
- `WS(strm)` casts `strm->workspace` to `struct inflate_workspace *`.

Control flow: No runtime logic except the accessor macro. `inflate.c` uses this to locate state/window from the caller-supplied workspace.

State and persistence:
- This is the full per-stream inflate persistent memory. Lifetime is controlled by the caller that owns `strm->workspace`.
- DFLTCC builds require `dfltcc_state` doubleword alignment, enforced by static assertion.

Dependencies and integration:
- Includes `<linux/zlib.h>`, and DFLTCC headers plus `<asm/page.h>` when configured.
- Used by `inflate.c` and workspace-size calculation.

Risks:
- Any struct layout change affects `zlib_inflate_workspacesize()` and DFLTCC `GET_DFLTCC_STATE()` assumptions.
- Callers must allocate at least `zlib_inflate_workspacesize()` bytes before `zlib_inflateInit2()`.

Test signals:
- Build with/without `CONFIG_ZLIB_DFLTCC`.
- Runtime allocation-size tests that initialize and reset streams repeatedly.

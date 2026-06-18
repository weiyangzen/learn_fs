# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutlib.h


Purpose: Declares the shared helper API implemented by `omap_voutlib.c` for OMAP video-output geometry and buffer management.

Important APIs/functions: The header exposes crop/window helpers (`omap_vout_default_crop()`, `omap_vout_new_crop()`, `omap_vout_try_window()`, `omap_vout_new_window()`, `omap_vout_new_format()`), low-level contiguous page helpers (`omap_vout_alloc_buffer()`, `omap_vout_free_buffer()`), and DSS-version predicates (`omap_vout_dss_omap24xx()`, `omap_vout_dss_omap34xx()`).

Control flow: Included by the main vout driver and VRFB backend so both paths share the same crop/window rules and buffer allocation behavior.

State and persistence: No state is stored in the header. All functions operate on caller-provided structs or return allocation addresses.

Dependencies/integration: Requires V4L2 pix/framebuffer/window/rect types and `u32`/`bool` definitions from included translation units. Its declarations mirror the library’s exported GPL symbols plus non-exported allocation/version helpers used in-tree.

Risks and test signals: Because this header does not include the types it uses, compile order depends on includers already having V4L2 and kernel type headers. Build-test each includer and verify prototypes stay synchronized with `omap_voutlib.c`.

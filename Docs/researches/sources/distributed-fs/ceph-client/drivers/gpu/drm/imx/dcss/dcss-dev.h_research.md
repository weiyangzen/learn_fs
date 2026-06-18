<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dev.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dev.h

Purpose: Provides the central private DCSS device contract, MMIO helpers, type data, context-loader identifiers, and submodule function declarations.

Important APIs/types/functions: Defines MMIO helper macros `dcss_writel/readl/set/clr/toggle/update`, `struct dcss_type_data`, `struct dcss_debug_reg`, `enum dcss_ctxld_ctx_type`, and `struct dcss_dev`. Declares driver/device lifecycle, PM ops, and APIs for BLKCTL, CTXLD, DPR, DTG, SS, scaler, and related modules.

Control flow: Header only, but its declarations define submodule call graph.

State and persistence behavior: `struct dcss_dev` is the persistent in-memory representation for the hardware instance, including clocks, submodule pointers, OF port, output type, and disable completion/callback state.

Dependencies: DRM fourcc/plane, Linux IO/PM, and videomode types.

Integration points: Included by all DCSS implementation files and KMS code. It is the shared private ABI for the DCSS driver.

Risks: The header exposes many internal submodule APIs without strong ownership boundaries. Changes to `struct dcss_dev` or context identifiers affect all submodules and PM paths.

Test signals: Build coverage across DCSS files, probe/resume exercising every declared submodule, and static analysis for missing prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dev.h -->

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/Kconfig

Purpose: Kconfig menu for Cadence DRM bridge drivers under the bridge/cadence directory.

Important APIs/types/functions: Defines `DRM_CDNS_DSI`, `DRM_CDNS_DSI_J721E`, `DRM_CDNS_MHDP8546`, and `DRM_CDNS_MHDP8546_J721E`. The DSI option selects KMS helper, MIPI DSI, panel bridge, generic PHY, generic MIPI DPHY, and videomode helpers, and depends on OF. The MHDP8546 DP option selects DP, HDCP, display, KMS, and panel bridge helpers, and depends on OF. J721E wrappers default to `y` under their parent options, with the DP wrapper limited to `ARCH_K3 || COMPILE_TEST`.

Control flow: Kconfig controls compile-time inclusion. Enabling parent symbols exposes the child wrapper options and drives Makefile object composition.

State and persistence: No runtime state. Persistent effect is kernel configuration.

Dependencies and integration: Integrates Cadence DSI and MHDP8546 bridge drivers with DRM, PHY, OF, panel bridge, DP/HDCP helpers, and TI K3/J721E wrappers.

Risks: Selects force helper dependencies on when the bridge is enabled; missing architecture constraints on the parent options may expose compile-test-only paths. Default-y wrapper symbols can include platform wrapper code whenever the parent is enabled.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, OF-disabled builds, parent-only versus wrapper-enabled builds, and module dependency checks validate this file.

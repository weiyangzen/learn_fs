<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Kconfig

Purpose: adds the `INTEL_MEI_HDCP` tristate configuration option for the MEI HDCP 2.2 services client.

Important APIs and types: the file defines one Kconfig symbol, `INTEL_MEI_HDCP`, with user-visible text "Intel HDCP2.2 services of ME Interface". It depends on `INTEL_MEI_ME` and on either `DRM_I915`, `DRM_XE`, or `COMPILE_TEST`.

Control flow: this is build-time configuration only. When enabled as built-in or module, the local Makefile builds `mei_hdcp.o`; otherwise the MEI HDCP client driver is omitted.

State and persistence: no runtime state. The selected Kconfig value is persisted in the kernel build configuration.

Dependencies and integration: ties the MEI HDCP module to the MEI ME PCI backend and to Intel display stacks that consume `i915_hdcp_ops`. The `DRM_XE` allowance means the client can be built even though this source still names i915 component interfaces.

Risks: dependency drift can break builds if display component interfaces move. Too-strict dependencies hide the driver on supported platforms; too-loose dependencies cause unresolved symbols or unusable modules.

Test signals: `make oldconfig` visibility, `CONFIG_INTEL_MEI_HDCP=m/y` builds, compile-test coverage without Intel display hardware, and module autoload on systems exposing the HDCP MEI UUID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Kconfig -->

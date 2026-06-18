<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Makefile

Purpose: builds the MEI HDCP client object when `CONFIG_INTEL_MEI_HDCP` is selected.

Important APIs and types: the single object rule is `obj-$(CONFIG_INTEL_MEI_HDCP) += mei_hdcp.o`.

Control flow: Kbuild includes `mei_hdcp.c` in the kernel or module according to the Kconfig tristate. No custom flags or multi-object composition are used.

State and persistence: no runtime state. Build output is controlled by the kernel configuration.

Dependencies and integration: relies on the surrounding MEI Kbuild hierarchy to descend into `hdcp/` and on Kconfig to ensure required MEI/display symbols are available.

Risks: if `mei_hdcp.c` grows into multiple source files, this Makefile must be updated to use an aggregate object list. Missing directory integration outside this file would silently skip the module even when Kconfig is set.

Test signals: `make M=drivers/misc/mei/hdcp`, full kernel builds with `CONFIG_INTEL_MEI_HDCP=m/y`, and checking that `mei_hdcp.ko` is emitted for modular builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hdcp/Makefile -->

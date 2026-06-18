<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Makefile

Purpose: Connects the Tyr Rust driver to kbuild.

Important APIs/types/functions: `obj-$(CONFIG_DRM_TYR) += tyr.o` builds the Rust module when selected.

Control flow: The Rust root module is `tyr.rs`, which kbuild compiles into `tyr.o`.

State and persistence: No runtime state.

Dependencies and integration points: Depends on the kernel Rust build system and the Kconfig option.

Risks and test signals: Build failures will surface when Rust module naming or source lists change. Module build tests are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Makefile -->

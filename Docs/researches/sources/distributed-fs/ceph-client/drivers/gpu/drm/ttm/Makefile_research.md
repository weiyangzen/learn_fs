# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/Makefile

Purpose: This kbuild file defines the object composition of the DRM TTM memory-management module and wires optional TTM KUnit tests into the build.

Important APIs, types, and functions: The primary kbuild variable is `ttm-y`, which collects core TTM object files: translation tables, buffer objects, buffer-object utilities and VM integration, module glue, execbuf utilities, range/resource/pool/device/system managers, and backup handling. `ttm-$(CONFIG_AGP)` conditionally adds `ttm_agp_backend.o`. `obj-$(CONFIG_DRM_TTM) += ttm.o` builds the aggregate module/object when TTM is enabled. `obj-$(CONFIG_DRM_TTM_KUNIT_TEST) += tests/` descends into the test directory when configured.

Control flow: Kbuild expands `ttm-y` into the linked contents of `ttm.o`. If AGP support is enabled, the AGP backend becomes part of that aggregate. If `CONFIG_DRM_TTM` is not enabled, no core TTM object is emitted from this Makefile. If KUnit testing is enabled, the nested tests Makefile is processed independently.

State and persistence: There is no runtime state in the Makefile. The persistent contract is build composition: changing object order or conditional membership changes what symbols are linked into `ttm.o` and whether tests are visible to KUnit.

Dependencies and integration points: Integrates with Linux kbuild, `CONFIG_DRM_TTM`, `CONFIG_AGP`, and `CONFIG_DRM_TTM_KUNIT_TEST`. Source objects named here implement the shared TTM API used by DRM drivers such as amdgpu, nouveau, i915, qxl, and others.

Risks: Omitting an object from `ttm-y` can create link-time missing symbols or subtler feature loss. Adding test descent without the right config would increase build scope unexpectedly. The AGP backend is correctly conditional; making it unconditional would break non-AGP builds.

Test signals: Build matrices should cover DRM_TTM as built-in and module, AGP enabled/disabled, and KUnit test enabled/disabled. Link output should contain exactly the expected TTM objects for each config.

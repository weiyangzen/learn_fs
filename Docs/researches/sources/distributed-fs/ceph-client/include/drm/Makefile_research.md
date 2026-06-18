# sources/distributed-fs/ceph-client/include/drm/Makefile

Purpose: defines the DRM header self-containment and kernel-doc validation build target.

Important APIs, types, and flow: `hdrtest-files` discovers all `*.h` headers under the DRM include directory. When `CONFIG_DRM_HEADER_TEST` is enabled, each header is transformed into a `.hdrtest` target. The command invokes the C compiler in syntax-only mode with the target header included twice to catch missing guards/self-contained include failures, then runs `kernel-doc -none` with optional `-Werror` under `CONFIG_WERROR` or `CONFIG_DRM_WERROR`, and touches the generated target.

State and persistence: no runtime state. Build artifacts are `.hdrtest` files in the object tree.

Dependencies and integration: integrates with Kbuild, `$(CC)`, `$(PYTHON3)`, `$(KERNELDOC)`, DRM header tree, and Kconfig options.

Risks and test signals: risks include shell discovery missing generated headers, false positives from non-self-contained headers, and Werror changing CI strictness. Signals include `CONFIG_DRM_HEADER_TEST=y` builds, header guard failures from double include, kernel-doc warnings, and matrix builds with DRM warning-as-error enabled.

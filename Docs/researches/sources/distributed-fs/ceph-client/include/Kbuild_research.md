# sources/distributed-fs/ceph-client/include/Kbuild

## Purpose
`include/Kbuild` exports top-level kernel headers selected by kbuild for generated UAPI/header-test workflows. In this tree it delegates DRM header test coverage.

## Important APIs, types, and functions
The only entry is `obj-$(CONFIG_DRM_HEADER_TEST) += drm/`, which descends into the `include/drm` subdirectory when DRM header tests are enabled.

## Control flow
During a kbuild pass with `CONFIG_DRM_HEADER_TEST=y` or module-equivalent test settings, kbuild evaluates this file and includes the DRM header-test directory in the build graph.

## State and persistence
No runtime state or persistent filesystem state exists.

## Dependencies and integration points
It integrates the repository's top-level include directory with the kernel build system and the DRM header-test configuration.

## Risks and test signals
Risks are limited to build graph omissions or accidental inclusion of headers under the wrong config. Test signals include builds with `CONFIG_DRM_HEADER_TEST` enabled and disabled.

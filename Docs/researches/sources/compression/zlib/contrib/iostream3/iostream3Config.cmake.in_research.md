# sources/compression/zlib/contrib/iostream3/iostream3Config.cmake.in

Purpose: defines the installed CMake package-loading logic for iostream3 consumers.

Important APIs/types/functions: `_iostreamv3_supported_components`, `find_dependency(ZLIB ...)`, includes of `iostreamv3-shared.cmake` and `iostreamv3-static.cmake`, and component found variables.

Control flow: if the consumer requests components, the config validates each component name, asks ZLIB for matching components, includes the corresponding export file optionally, and marks missing components as package-not-found. Without components, it finds ZLIB, includes both component exports if present, and then requires both shared and static targets to exist.

State and persistence: sets CMake package variables such as `iostreamv3_FOUND`, `iostreamv3_NOT_FOUND_MESSAGE`, and `iostreamv3_<component>_FOUND` during configuration.

Dependencies/integration: consumed by `find_package(iostreamv3 CONFIG)`, depends on `CMakeFindDependencyMacro` and installed export files.

Risks: the `else(iostream3_FIND_COMPONENTS)` argument uses `iostream3` instead of `iostreamv3`, which is harmless to CMake parsing but misleading. The no-components path fails unless both shared and static targets exist, so users must request a component when only one library variant was installed.

Test signals: package behavior is covered by generated find-package tests, including no-components and wrong-components cases.

# sources/compression/zlib/contrib/ada/cmake/Modules/CMakeADAInformation.cmake

Purpose: CMake language information module defining compile, bind, link, static archive, and helper functions for Ada targets.

Important APIs/functions: sets Ada output extension and per-config flags; defines `CMAKE_ADA_CREATE_SHARED_LIBRARY`, `CMAKE_ADA_CREATE_STATIC_LIBRARY`, `CMAKE_ADA_COMPILE_OBJECT`, and `CMAKE_ADA_LINK_EXECUTABLE`; exposes `ada_add_executable`, `ada_add_library`, and `ada_find_ali`.

Control flow: initializes language flags from `ADAFLAGS`, applies optional user rule overrides, configures standard libraries and launchers, installs custom rule commands that call helper scripts, and wraps normal CMake targets to add ALI cleanup files and `-aO` link options.

State and persistence: modifies CMake target properties including `ADDITIONAL_CLEAN_FILES`, `ALI_FLAG`, `LINK_FLAGS`, and link options. Generated Ada binder artifacts are marked for cleanup.

Dependencies and integration: depends on CMake internal modules `CMakeLanguageInformation`, `CMakeCommonLanguageInclude`, and helper scripts in `contrib/ada/cmake`.

Risks: function loops use argument ranges and source-name string replacement that assume `.adb` source paths and simple names. Target `LINK_FLAGS` assembly from linked libraries can be fragile for transitive dependencies.

Test signals: Ada contrib builds and tests exercise compile/link rules for shared/static libraries and executables.

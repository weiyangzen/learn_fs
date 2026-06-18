# sources/compression/zlib/contrib/CMakeLists.txt

Purpose: option dispatcher for zlib contrib features and sub-libraries in the root CMake build.

Important APIs/functions: defines `zlib_add_contrib_lib(name description dir)` and `zlib_add_contrib_feature(name description dir [default])`. Sets `WORK_DIR`, `ZLIB_CONTRIB_PREFIX`, and `inst_setup`, then declares feature/library options for GVMAT64, INFBACK9, CRC32VX, ADA, BLAST, IOSTREAM3, MINIZIP, PUFF, TESTZLIB, and ZLIB1_DLL.

Control flow: contrib libraries inherit root shared/static/testing/install options unless explicitly set, then add their subdirectory only when enabled. Feature toggles add subdirectories directly. Windows-only blocks expose testzlib and legacy zlib1-dll support.

State and persistence: CMake cache options control which contrib directories participate in the build.

Dependencies and integration: included unconditionally by root `CMakeLists.txt`; delegates to each contrib subproject. CRC32VX can modify root zlib targets by adding source files.

Risks: `ZLIB_BUILD_ZLIB1_DLL` is checked before its `option()` declaration, so the first configure relies on an externally supplied value or defaults to no subdirectory until reconfigure. Global `WORK_DIR`/prefix variables are shared by subprojects.

Test signals: `contribs.yml` validates all-contrib and standalone contrib configurations.

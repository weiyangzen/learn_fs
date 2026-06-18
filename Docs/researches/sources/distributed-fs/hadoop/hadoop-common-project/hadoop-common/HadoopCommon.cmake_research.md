# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/HadoopCommon.cmake

Purpose: Shared CMake utility and platform configuration module for Hadoop native components. It centralizes compiler/linker flags, dual static/shared library helpers, output directories, library suffix search behavior, and OS/architecture-specific native build handling.

Important APIs and control flow: macros `hadoop_add_compiler_flags` and `hadoop_add_linker_flags` append flags to global C/C++ and executable/shared linker variables. Functions `hadoop_add_dual_library`, `hadoop_target_link_dual_libraries`, `hadoop_output_directory`, and `hadoop_dual_output_directory` create and configure paired shared/static targets. Library suffix macros adjust `CMAKE_FIND_LIBRARY_SUFFIXES` for versioned or unversioned shared library discovery across Darwin, FreeBSD, Windows, and Unix.

State and dependencies: state is CMake cache/global variables: compiler flags, linker flags, target properties, `CMAKE_SYSTEM_PROCESSOR`, `CMAKE_LIBRARY_ARCHITECTURE`, and C standard. Dependencies include CMake thread detection, `readelf`, `JAVA_JVM_LIBRARY`, `CheckSymbolExists`, and platform identifiers.

Integration points: included by native subprojects before JNI/native library builds. Linux logic adds `_GNU_SOURCE`, suppresses GCC 14 implicit-function-declaration-as-error, handles 32-bit JVM builds with `-m32`, and detects ARM soft-float JVM ABI. Solaris logic requires 64-bit JVM, gcc, POSIX/extension flags, C++98, and processor remapping to amd64/sparcv9.

Risks and test signals: global mutation of flags and processor variables affects all later CMake discovery, especially `FindJNI`. ARM soft-float detection depends on `readelf` and `JAVA_JVM_LIBRARY` being available. The GCC 14 warning suppression may hide real implicit declaration problems while preserving legacy build compatibility.

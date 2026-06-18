# sources/compression/zlib/contrib/ada/cmake/static_link_helper.cmake

Purpose: CMake script wrapper for creating Ada static libraries.

Important inputs: archiver path in `CMAKE_ARGV3`, output archive in `CMAKE_ARGV4`, and object files in subsequent arguments.

Control flow: validates the archiver, collects object file arguments except the final CMake sentinel, then runs `${ar} rcs <archive> <objects>`.

State and persistence: writes the static archive target.

Dependencies and integration: used by `CMAKE_ADA_CREATE_STATIC_LIBRARY`; typically receives `CMAKE_AR`.

Risks: the `foreach` starts at range 5 but also has a second range expression ending at `CMAKE_ARGC`; positional mistakes can omit or include unintended arguments. Error message says “linker not set” although the tool is an archiver.

Test signals: static Ada target and static Ada tests link against archives produced here.

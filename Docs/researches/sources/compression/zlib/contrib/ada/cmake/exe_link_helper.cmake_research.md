# sources/compression/zlib/contrib/ada/cmake/exe_link_helper.cmake

Purpose: CMake script wrapper around GNAT executable linking.

Important inputs: linker/compiler in `CMAKE_ARGV3`, output in `CMAKE_ARGV4`, `OBJ` and `LIBS` sentinels separating object and library arguments.

Control flow: scans arguments to find the first object, converts it to an ALI path, collects non-ALI flags and libraries, then runs `${linker} link <ali> -o <output> <flags> <objects> <libs>`.

State and persistence: produces the Ada executable target.

Dependencies and integration: used by `CMAKE_ADA_LINK_EXECUTABLE`.

Risks: `OTHER_OBJECTS` is referenced but not populated in the script, so extra non-main objects may be omitted unless GNAT resolves them from ALI metadata. The first-object-to-ALI heuristic assumes object ordering has the main unit first.

Test signals: Ada test/demos link through this helper, exposing argument parsing or library lookup failures.

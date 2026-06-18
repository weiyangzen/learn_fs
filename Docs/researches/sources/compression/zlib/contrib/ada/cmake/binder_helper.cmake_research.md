# sources/compression/zlib/contrib/ada/cmake/binder_helper.cmake

Purpose: CMake script wrapper around GNAT binding for Ada object/ALI files.

Important inputs: expects `CMAKE_ARGV3` as binder/compiler command and `CMAKE_ARGV4` as an object path convertible to `.ali`. Parses later arguments after `FLAGS` while ignoring `-O` output flags.

Control flow: derives the ALI filename and search path, appends `-aO<search_path>`, attempts `gnat bind`, retries with `bind -n` if no main function is present, fails on binder errors, and touches the original object path for CMake dependency satisfaction.

State and persistence: creates or updates binder artifacts through GNAT and touches the target object path.

Dependencies and integration: used by `CMAKE_ADA_CREATE_SHARED_LIBRARY` and `CMAKE_ADA_LINK_EXECUTABLE` rules.

Risks: argument parsing is positional and assumes CMake command templates. `RESULT` is only set on the retry path; if the first bind succeeds, the later `if(RESULT)` relies on unset variable behavior.

Test signals: Ada executable/library link steps fail early if binding cannot resolve ALI files or main/no-main mode.

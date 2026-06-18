# sources/distributed-fs/lizardfs/src/devtools/CMakeLists.txt

Purpose: builds the `devtools` support library and includes the CRC utility subdirectory.

Important APIs/functions: `aux_source_directory(${CMAKE_CURRENT_SOURCE_DIR} DEVTOOLS_SOURCES)`, `add_library(devtools ${DEVTOOLS_SOURCES})`, `add_subdirectory(mycrc32)`.

Control flow: all source files directly in `src/devtools` are collected into a library; `mycrc32` is built separately as an executable.

State and persistence: build configuration only.

Dependencies and integration: library contains headers/sources such as request logging and trace helpers when enabled by compile definitions.

Risks: `aux_source_directory` can silently pick up new files and is less explicit than target source lists.

Test signals: build success is the primary signal.

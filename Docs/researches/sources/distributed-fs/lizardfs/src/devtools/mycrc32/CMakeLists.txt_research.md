# sources/distributed-fs/lizardfs/src/devtools/mycrc32/CMakeLists.txt

Purpose: build definition for the `mycrc32` command-line utility.

Important APIs/functions: collects local sources into `MYCRC32_SOURCES`, creates executable `mycrc32`, and links it with `mfscommon`.

Control flow: CMake build-only; no install rule in this file.

State and persistence: build target definition only.

Dependencies and integration: utility depends on common CRC implementation from `mfscommon`.

Risks: `aux_source_directory` can include unintended future files.

Test signals: build/link success.

# sources/distributed-fs/lizardfs/src/devtools/Empty.cc

Purpose: placeholder C++ translation unit for the `devtools` library.

Important APIs/functions: contains only the platform include and license header; exports no symbols.

Control flow: none.

State and persistence: none.

Dependencies and integration: included by `aux_source_directory` so the `devtools` library has at least one source even when most functionality is header-only or compile-flag-gated.

Risks: no behavioral risk; its presence can hide that a library is effectively header-only.

Test signals: compile-only.

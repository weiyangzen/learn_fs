# sources/distributed-fs/openafs/src/WINNT/tests/torture/Stress/StdAfx.h

Purpose: Visual C++ precompiled-header placeholder for the `Stress` launcher project.

Important APIs and types: only an include guard and optional `#pragma once` for MSVC versions greater than 1000 are active. The body contains the standard Visual Studio insertion marker for project-specific includes.

Control flow: none at runtime.

State and persistence: none.

Dependencies and integration: included by older Visual Studio project configurations to satisfy PCH build settings. It deliberately does not pull in Windows headers; `Stress.c` includes its own dependencies.

Risks and test signals: low code risk, but project settings may depend on this file existing. Build success of the legacy VC project is the primary signal.

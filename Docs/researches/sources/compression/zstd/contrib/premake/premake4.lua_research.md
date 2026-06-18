<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/premake/premake4.lua -->
# sources/compression/zstd/contrib/premake/premake4.lua

## Purpose
This is a minimal GENie/premake4 example that loads the zstd premake helper and instantiates a sample solution.

## Important APIs, Types, And Functions
It calls `dofile('zstd.lua')`, defines solution `example`, declares `Debug`/`Release` configurations, and calls `project_zstd('../../lib/')`.

## Control Flow
Premake evaluates the helper file first, then executes `project_zstd` to create a static zstd library project against the relative lib directory.

## State And Persistence
It writes no state itself; premake generation creates project files externally when invoked.

## Dependencies And Integration Points
It depends on premake4/GENie and the adjacent `zstd.lua`. It demonstrates how downstream users can embed zstd as a generated static library.

## Risks
The hard-coded relative path only works from the contrib/premake location. This file is an example, not a production multi-platform project definition.

## Test Signals
Running premake/GENie from this directory should generate a solution containing the zstd static library target.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/premake/premake4.lua -->

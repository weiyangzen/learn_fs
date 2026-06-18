<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/charts.h -->
# sources/distributed-fs/lizardfs/src/common/charts.h

## Purpose

This header defines the chart subsystem's public constants, chart definition structures, expression macros, and rendering/storage API.

## Important APIs, Types, and Functions

Important macros define aggregation modes, scales, expression opcodes, direct/calc chart ids, `CHARTS_NODATA`, and helper expression builders such as `CHARTS_ADD`, `CHARTS_DIV`, and `CHARTS_CALCDEF`. `statdef` describes direct series; `estatdef` describes extended three-color charts. Public functions mirror the implementation in `charts.cc`.

## Control Flow

The header is declarative, but the macros are used to build reverse-polish calculation programs consumed by `charts_filltab()`.

## State and Persistence Behavior

Chart definitions passed to `charts_init()` define how runtime series are stored and persisted. `CHARTS_NODATA` is the sentinel value for missing samples.

## Dependencies and Integration Points

It includes integer and stdio headers and is consumed by services that publish charts to CGI/status endpoints.

## Risks and Edge Cases

`CHARTS_SUB(x,y)` expands to `CHARTS_OP_ADD`, which appears inconsistent with the `CHARTS_OP_SUB` opcode and can silently compute wrong calculated charts. Macro expression programs are untyped and validated only at runtime.

## Test Signals

Tests should compile representative `STATDEFS`, `CALCDEFS`, and `ESTATDEFS`, verify all arithmetic opcodes, and render direct and calculated charts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/charts.h -->

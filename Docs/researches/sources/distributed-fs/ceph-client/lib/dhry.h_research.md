# sources/distributed-fs/ceph-client/lib/dhry.h

## Purpose
Defines the common data model and function prototypes for the kernel's Dhrystone 2.1 benchmark implementation.

## APIs, Types, and Functions
The header documents the benchmark history and measurement rules, then defines `Enumeration`, integer aliases, `Capital_Letter`, `Boolean`, `Str_30`, one- and two-dimensional array types, and `struct record`/`Rec_Type`/`Rec_Pointer` with a discriminated-union-like variant. It declares globals `Int_Glob` and `Ch_1_Glob`, procedures `Proc_6`, `Proc_7`, `Proc_8`, functions `Func_1`, `Func_2`, and benchmark entry `dhry(int n)`.

## Control Flow
The header has no executable flow. It fixes the shared types and prototypes used by `dhry_1.c`, `dhry_2.c`, and `dhry_run.c`.

## State and Persistence
The declared globals are defined in `dhry_1.c`. Type definitions have no runtime state.

## Dependencies and Integration Points
It is included by both benchmark implementation files and by the module runner. It integrates Dhrystone's historical C benchmark structure with kernel allocation, timing, and module-parameter wrappers.

## Risks and Test Signals
Risks include changing types or prototypes in a way that invalidates Dhrystone comparability, making optimization easier than intended, or breaking separate compilation assumptions. Test signals include successful builds of all Dhrystone files, benchmark self-check output from `dhry()`, and sanity comparisons of reported Dhrystones per second across iterations.

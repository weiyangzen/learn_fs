# sources/distributed-fs/ceph-client/tools/perf/util/print_insn.c

## Purpose
This file prints sampled instruction bytes either as raw hex or as assembly using the capstone-backed disassembler.

## Important APIs, Types, and Functions
Exports are `sample__fprintf_insn_raw`, `fprintf_insn_asm`, and `sample__fprintf_insn_asm`. Internal `is64bitip` decides disassembler bitness from the mapped DSO or normalized machine architecture.

## Control Flow
Raw printing iterates `sample->insn` and emits two-digit hex bytes separated by spaces. Assembly printing delegates to `capstone__fprintf_insn_asm`. Sample assembly printing computes 64-bit mode, calls the disassembler with sample CPU mode, instruction buffer, length, and IP, and falls back to raw hex when disassembly returns an error.

## State and Persistence
No state is stored. All behavior depends on the passed sample, thread, machine, address location, and capstone backend.

## Dependencies and Integration Points
It depends on perf sample structures, machine/thread/map/dso metadata, capstone wrapper, and dump-insn output conventions. It is used by script/report paths that display sampled instruction bytes.

## Risks
Bitness fallback is heuristic when no DSO is mapped. Capstone availability and architecture support determine assembly quality. Invalid sample instruction lengths or buffers can affect output.

## Test Signals
Tests should cover raw output spacing, assembly fallback on disassembler error, DSO-derived 32/64-bit selection, and normalized machine-name fallback for x86_64, arm64, and s390.

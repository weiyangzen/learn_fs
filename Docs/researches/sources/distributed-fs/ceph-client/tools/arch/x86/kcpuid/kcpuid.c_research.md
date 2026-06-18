# sources/distributed-fs/ceph-client/tools/arch/x86/kcpuid/kcpuid.c

## Purpose
Implements `kcpuid`, a CPUID introspection tool that collects supported CPUID leaves/subleaves on the current CPU, annotates them with CSV metadata, and prints flags, fields, details, or raw register values.

## APIs, Types, and Functions
Key data types are `bits_desc`, `reg_desc`, `subleaf`, `cpuid_func`, and `cpuid_range`. Important functions include `setup_cpuid_range()`, `cpuid_store()`, `parse_line()`, `parse_text()`, `show_reg()`, `show_leaf()`, `show_info()`, `parse_options()`, and `main()`. Options include `--all`, `--bitflags`, `--detail`, `--file`, `--leaf`, `--raw`, and `--subleaf`.

## Control Flow, State, and Persistence
`main()` parses options, probes standard/extended/Transmeta/Centaur ranges, allocates per-leaf arrays, stores nonzero CPUID outputs, parses `/usr/share/misc/cpuid.csv` or `./cpuid.csv`, attaches field descriptions only for supported leaves, then prints according to options. Subleaf handling is capped and leaf-specific: some leaves derive counts from EAX, while others use fixed limits.

## Dependencies and Integration
Uses GCC `<cpuid.h>` `__cpuid_count()`, libc allocation/string/getopt APIs, and external CSV metadata. The Makefile installs the binary and CSV together.

## Risks and Test Signals
Risks include fixed 32-description slots per register overflowing on dense CSV rows, simplistic comma parsing that cannot handle quoted commas, memory not freed by design, missing subleaf count rules for new CPUID leaves, and raw mode skipping CSV validation. Test signals are raw dumps on representative CPUs, CSV parser tests for ranges and malformed lines, `--leaf/--subleaf` boundary tests, and comparison with kernel CPUID feature exposure.

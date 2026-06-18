# sources/distributed-fs/ceph-client/tools/arch/x86/tools/gen-cpu-feature-names-x86.awk

## Purpose
Generates a C array mapping x86 CPU feature and bug bit positions to macro names by scanning `cpufeatures.h`.

## APIs, Types, and Functions
The script has no reusable functions. It emits `static const char *cpu_feature_names[(NCAPINTS+NBUGINTS)*32]`, fills entries for `#define X86_FEATURE_*`, and fills bug entries for `#define X86_BUG_*`.

## Control Flow, State, and Persistence
`BEGIN` prints the header and initializes a regex for parenthesized numeric expressions. Pattern rules match feature and bug defines, extract the bit expression from parentheses, and print designated initializers. `END` closes the array.

## Dependencies and Integration
Consumes `tools/arch/x86/include/asm/cpufeatures.h`. Integrated into tools builds that need symbolic CPU feature names without maintaining a separate table.

## Risks and Test Signals
Risks include regex failure on nonstandard macro formatting, missing aliases whose values are not parenthesized, and generating macro names rather than `/proc/cpuinfo` strings. Test signals are running the generator on the current header, compiling the output, and checking representative feature and bug indices.

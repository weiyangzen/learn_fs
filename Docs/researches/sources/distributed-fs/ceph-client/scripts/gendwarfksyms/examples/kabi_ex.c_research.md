# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi_ex.c

## Purpose
`examples/kabi_ex.c` instantiates variables for the kABI example types so DWARF contains concrete exported-like symbols to inspect.

## Important APIs, Types, and Functions
It includes `kabi_ex.h` and defines global variables of `struct s`, `enum e`, `ex0*` through `ex5*`, and integer `ex6a`.

## Control Flow
There is no executable control flow; the declarations force compiler emission of DWARF type information.

## State and Persistence Behavior
The compiled object contains global symbols and DWARF/debug section state used by example validation.

## Dependencies and Integration Points
The file is consumed by the documented example commands in `kabi_ex.h`, often piping `nm` output into `gendwarfksyms --stable`.

## Risks and Test Signals
Compiler optimization/debug flags can affect DWARF emission. Test with `gcc -g -c examples/kabi_ex.c` and the FileCheck commands documented in the header.

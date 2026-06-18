# sources/distributed-fs/ceph-client/drivers/staging/nvec/Makefile

## Purpose
Kbuild object mapping for the NVEC MFD stack.

## Important APIs, Types, And Functions
Builds `nvec.o`, `nvec_kbd.o`, `nvec_ps2.o`, `nvec_power.o`, and `nvec_paz00.o` from their matching Kconfig symbols.

## Control Flow
When a symbol is enabled, Kbuild includes the corresponding source in the kernel or builds it as a module.

## State And Persistence
No runtime state. Build artifacts and module names are determined by object filenames.

## Dependencies And Integration Points
Consumes the symbols declared in `Kconfig` and feeds kernel module linking.

## Risks
The modules are independent objects, so child modules can be loaded separately but still require the parent MFD device at runtime.

## Test Signals
Build each Kconfig combination and verify generated modules: `nvec`, `nvec_kbd`, `nvec_ps2`, `nvec_power`, and `nvec_paz00`.

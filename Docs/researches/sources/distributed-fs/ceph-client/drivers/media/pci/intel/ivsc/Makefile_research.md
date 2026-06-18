# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/Makefile

## Purpose
This Makefile builds the Intel IVSC MEI client drivers.

## Important APIs, Types, And Data
When `CONFIG_INTEL_VSC` is enabled, it builds two modules/objects: `ivsc-csi.o` from `mei_csi.o` and `ivsc-ace.o` from `mei_ace.o`.

## Control Flow
There is no runtime flow. The file maps the single Kconfig symbol to the two logical IVSC drivers described in Kconfig.

## State And Persistence
No state is represented.

## Dependencies And Integration Points
The module names align with Kconfig help text and MEI client driver registration inside the C files.

## Risks And Test Signals
Build tests should confirm both modules are produced for `m` and linked for `y`, and that module names match expected autoload behavior.

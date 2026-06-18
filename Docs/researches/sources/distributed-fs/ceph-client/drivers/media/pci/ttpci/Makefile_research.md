<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Makefile

## Purpose
`ttpci/Makefile` maps TTPci budget Kconfig symbols to kernel objects and sets include paths for DVB frontend, tuner, and common media headers.

## Important APIs, Types, and Functions
Object mappings are `budget-core.o`, `budget.o`, `budget-av.o`, and `budget-ci.o` under their corresponding `CONFIG_DVB_*` symbols. `ccflags-y` adds `drivers/media/dvb-frontends/`, `drivers/media/tuners`, and `drivers/media/common`.

## Control Flow
There is no runtime control flow. Kbuild uses this file to compile selected modules and provide include search paths for board-specific frontend headers.

## State and Persistence
The file owns build metadata only. It creates no runtime or persistent kernel state.

## Dependencies and Integration Points
It integrates with Kbuild and the Kconfig options in the same directory. The include paths support direct includes such as `stv0299.h`, `tda1004x.h`, tuner headers, and common TTPci EEPROM support.

## Risks and Edge Cases
Header include paths are broad and may hide missing explicit relative includes. Object selection must stay aligned with Kconfig symbol names and help text module names.

## Test Signals
Validate `make M=drivers/media/pci/ttpci` for each symbol combination, module filenames, and successful builds after moving frontend/tuner/common headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/Makefile -->

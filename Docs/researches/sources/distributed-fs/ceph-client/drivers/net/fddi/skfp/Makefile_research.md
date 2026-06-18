# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/Makefile

## Purpose
Builds the SysKonnect FDDI PCI adapter driver object within the Linux kernel Kbuild system. It declares the `skfp.o` composite object when `CONFIG_SKFP` is enabled and lists the driver, hardware module, SMT, queue, timer, resource-management, and optional ESS object files that form the final module/built-in object.

## Important APIs, Types, And Functions
The public build interface is Kbuild syntax. `obj-$(CONFIG_SKFP) += skfp.o` gates compilation on the kernel configuration symbol. `skfp-objs := ...` declares the object aggregation list: `skfddi.o`, `hwmtm.o`, `fplustm.o`, `smt.o`, `cfm.o`, `ecm.o`, `pcmplc.o`, `pmf.o`, `queue.o`, `rmt.o`, `smtdef.o`, `smtinit.o`, `smttimer.o`, `srf.o`, `hwt.o`, `drvfbi.o`, and `ess.o`. `ccflags-y` adds `-DPCI`, `-DMEM_MAPPED_IO`, and suppresses strict-prototype warnings.

## Control Flow
There is no runtime control flow. During kernel builds, Kbuild evaluates `CONFIG_SKFP`, compiles each listed source into an object, then links them into `skfp.o`. The preprocessor flags select PCI and memory-mapped I/O code paths inside the SysKonnect sources.

## State And Persistence Behavior
The file has no runtime state. Its state effect is build-system state: enabling or disabling the composite driver and changing preprocessor symbols for all sources in this directory. Build outputs persist only as normal generated kernel objects outside the source file.

## Dependencies And Integration Points
This integrates with Linux Kbuild and the kernel configuration symbol `CONFIG_SKFP`. It assumes all listed `.c` files are present in the same directory and are compatible with `-DPCI -DMEM_MAPPED_IO`. The comment documents an intentional integration constraint: the hardware module source is shared with other projects, so warning cleanup is avoided to preserve common code.

## Risks
Object-list drift can silently omit driver subsystems or fail the build if a file is renamed. The global `ccflags-y` affects all listed objects, so changing it can alter hardware access mode or platform assumptions throughout the driver. Suppressing `-Wstrict-prototypes` can hide prototype quality issues, but the comment indicates this is a deliberate tradeoff for shared vendor code.

## Test Signals
Build with `CONFIG_SKFP=m` and `CONFIG_SKFP=y` to confirm both module and built-in paths link. Inspect the compile command for `-DPCI -DMEM_MAPPED_IO`. A clean build should produce `skfp.o` from all listed objects without missing-symbol errors.

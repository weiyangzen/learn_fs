# sources/distributed-fs/ceph-client/drivers/misc/ocxl/Makefile

## Purpose
This Makefile defines the OCXL composite module object list and build flags.

## Important APIs, types, and functions
`ocxl-y` includes `main.o`, `pci.o`, `config.o`, `file.o`, `pasid.o`, `mmio.o`, `link.o`, `context.o`, `afu_irq.o`, `sysfs.o`, `trace.o`, and `core.o`. `obj-$(CONFIG_OCXL) += ocxl.o` builds the module/built-in. `ccflags-$(CONFIG_PPC_WERROR) += -Werror`, and `CFLAGS_trace.o := -I$(src)` supports tracepoint include lookup.

## Control flow and state
There is no runtime flow. Build order collects OCXL subsystems into one module.

## State and persistence behavior
No runtime state exists here.

## Dependencies and integration points
It integrates with Kbuild, `CONFIG_OCXL`, PowerPC warning policy, and the tracepoint build infrastructure.

## Risks and test signals
Risks include missing object files from the composite module, trace include breakage, and Werror-only build failures. Test signals include `CONFIG_OCXL=m/y` builds and tracepoint compilation.

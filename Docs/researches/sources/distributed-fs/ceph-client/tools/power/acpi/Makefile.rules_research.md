<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/Makefile.rules -->
# sources/distributed-fs/ceph-client/tools/power/acpi/Makefile.rules

## Purpose
Shared build/install rules for ACPI userspace tools. It maps a `TOOL` and `TOOL_OBJS` list into an output object directory, builds the tool, stages copied ACPICA kernel headers, and provides common clean/install/uninstall targets.

## Important APIs, Types, And Functions
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## Control Flow
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## State And Persistence
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## Dependencies And Integration Points
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## Risks And Edge Cases
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.

## Test Signals
Control flow builds `$(OUTPUT)$(TOOL)` from `$(toolobjs)`, compiles `%.c` via the configured `vpath`, creates `$(KERNEL_INCLUDE)` by copying `include/acpi`, and installs tools under `$(sbindir)`. State is build output, copied headers, and installed binaries/manpage extras from caller variables. Dependencies are `Makefile.config`, `srctree`, compiler/linker variables, and caller-defined `EXTRA_INSTALL`. Risks include stale copied ACPICA headers, `find | xargs rm` behavior with empty lists, and shared output directories colliding between tools. Test signals are per-tool compile, clean removing objects and copied includes, and DESTDIR install/uninstall checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/Makefile.rules -->

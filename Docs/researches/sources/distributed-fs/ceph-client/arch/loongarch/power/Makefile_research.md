<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/Makefile -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/Makefile

### Purpose
This Makefile selects LoongArch platform power-management objects.

### Important APIs, Types, And Functions
Rules are `obj-y += platform.o`, `obj-$(CONFIG_SUSPEND) += suspend.o suspend_asm.o`, and `obj-$(CONFIG_HIBERNATION) += hibernate.o hibernate_asm.o`.

### Control Flow
Platform support is always built; suspend and hibernation support are conditional on their kernel config options.

### State, Persistence, And Dependencies
No runtime state exists. It depends on Kbuild and PM config symbols.

### Integration Points
Controls whether ACPI S3 and swsusp architecture hooks are available.

### Risks
Incorrect selection can leave unresolved symbols between C and assembly halves of suspend/hibernate.

### Test Signals
Cross-build with suspend and hibernation enabled/disabled independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/Makefile -->

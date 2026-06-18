# sources/distributed-fs/ceph-client/drivers/acpi/x86/Makefile

### Purpose
This Makefile selects the x86-specific ACPI support objects that are linked into the ACPI x86 helper object or built independently for x86 blacklist handling.

### Important APIs, Types, And Functions
There are no runtime APIs. Build variables add `apple.o`, `cmos_rtc.o`, `s2idle.o`, and `utils.o` to `acpi-x86.o`, add `lpss.o` only with `CONFIG_PCI`, and build `blacklist.o` when `CONFIG_X86` is enabled.

### Control Flow
Build-time control flow is Kbuild conditional expansion. `obj-$(CONFIG_ACPI)` emits `acpi-x86.o`; `acpi-x86-$(CONFIG_PCI)` gates LPSS support because it depends on PCI helpers and device-link cases.

### State, Persistence, And Dependencies
No runtime state exists. The file encodes compile-time dependencies between x86 ACPI helpers and kernel configuration symbols.

### Integration Points
It feeds the ACPI driver subtree build and determines whether Apple property extraction, CMOS RTC address-space handling, LPSS, s2idle LPS0, and x86 utility quirks are available to ACPI core code.

### Risks
Incorrect gating can cause unresolved symbols or silently omit platform quirks. `blacklist.o` is linked outside `acpi-x86.o`, so changes to ACPI-vs-X86 conditions can affect early blacklist behavior.

### Test Signals
Build matrix coverage with `CONFIG_ACPI`, `CONFIG_X86`, `CONFIG_PCI`, and `CONFIG_X86_INTEL_LPSS` combinations should verify objects are present only when expected and no symbols are missing.

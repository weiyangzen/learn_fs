<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidbg/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidbg/Makefile

## Purpose
Builds the `acpidbg` userspace AML debugger bridge. It includes ACPI Makefile configuration, sets `TOOL=acpidbg`, searches ACPICA/common/service-layer sources through `vpath`, adds `-DACPI_APPLICATION -DACPI_SINGLE_THREAD -DACPI_DEBUGGER`, links pthread, and delegates rules to `Makefile.rules`.

## Important APIs, Types, And Functions
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## Control Flow
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## State And Persistence
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## Dependencies And Integration Points
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## Risks And Edge Cases
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.

## Test Signals
The build produces one object, `acpidbg.o`, but inherits common output, install, and copied-header behavior. State is object/binary output. Dependencies are ACPICA headers, the kernel `circ_buf.h`, pthread linkage, and the common rule file. Risks include macro mismatch (`ACPI_SINGLE_THREAD` versus code paths expecting `ACPI_SINGLE_THREADED` elsewhere), debugfs interface availability only at runtime, and broad `vpath` hiding source selection mistakes. Test signals are successful build, link with pthread, and `acpidbg -h` plus open-failure behavior when debugfs is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidbg/Makefile -->

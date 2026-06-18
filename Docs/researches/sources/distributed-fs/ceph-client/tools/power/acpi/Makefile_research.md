<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/acpi/Makefile

## Purpose
Top-level ACPI tools make entry point. It imports the common scripts include, declares `.NOTPARALLEL`, and fans out `all`, `clean`, `install`, and `uninstall` to `acpidbg`, `acpidump`, `ec`, and `pfrut` subdirectories through the kernel `descend` macro.

## Important APIs, Types, And Functions
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## Control Flow
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## State And Persistence
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## Dependencies And Integration Points
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## Risks And Edge Cases
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.

## Test Signals
Control flow is target delegation only: aggregate targets expand to subtool targets and call `$(call descend,tools/$@,all)` or the derived clean/install/uninstall form. There is no runtime state; build state lives in subtool output directories. Dependencies are `../../scripts/Makefile.include` and each subtool Makefile. Risks include serialized builds due to `.NOTPARALLEL`, subtool naming assumptions in `$(@:_clean=)` substitutions, and install failure if a platform lacks one subtool dependency. Test signals are `make`, `make clean`, staged `make install DESTDIR=...`, and verifying each expected binary target is invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/Makefile -->

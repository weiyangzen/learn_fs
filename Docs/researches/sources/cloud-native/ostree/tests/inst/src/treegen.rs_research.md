<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/treegen.rs -->
## sources/cloud-native/ostree/tests/inst/src/treegen.rs

Purpose: generates synthetic root trees and mutates executable content for update/transaction tests.

Important APIs/functions: `mkroot()` and `mkvroot()` create deterministic versioned trees; `is_elf()` checks the ELF magic; `mutate_one_executable_to()` atomically writes a modified copy preserving permissions; `mutate_executables_to()` samples executable ELF candidates; `update_os_tree()` commits changed root content to an OSTree ref.

Control flow/state: `mkroot()` persists a version counter in `etc/.mkrootversion`. `update_os_tree()` creates a tempdir under repo `tmp`, scans `/usr/bin`, `/usr/lib`, `/usr/lib64`, mutates at least one eligible ELF, and commits with ownership, SELinux-from-base, link speedup, no bindings, and no xattrs.

Dependencies/integration: uses `cap-std-ext`, `rand`, `xshell`, and shared `write_file()`. Called by auth and destructive transaction tests.

Risks/test signals: candidate filter appears to require setuid/setgid bits due to the mode condition, which may limit mutations unexpectedly. Main signal is `mutated > 0` and successful `ostree commit`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/inst/src/treegen.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix_test.go

Purpose: Unix security regression tests for CVE-2018-15664 style malicious symlink paths.

Important APIs/types/functions: `TestUntarWithMaliciousSymlinks`, `TestTarWithMaliciousSymlinks`, and `isDataInTar`.

Control flow: `TestUntarWithMaliciousSymlinks` creates a root containing a symlink to a host-controlled parent and verifies `UntarWithRoot(..., root)` does not overwrite the host file, while deliberately using the symlink as root demonstrates the misuse can overwrite. `TestTarWithMaliciousSymlinks` attempts several path/include combinations and verifies host file data is not leaked into tar output when using the safe root.

State/persistence: temporary root/host files/symlinks only.

Dependencies/integration: exercises `UntarWithRoot`, `Tar`, `archive.TarWithOptions`, Unix symlinks, and tar readers.

Risks/test signal: high-value tests for chroot confinement and symlink race avoidance. They make the intended root trust boundary explicit: the root must not be attacker controlled.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix_test.go -->

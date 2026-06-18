# sources/cloud-native/ostree/src/libostree/ostree-libarchive-private.h

## Purpose
This private header centralizes libarchive cleanup typedefs and small archive-opening helpers for OSTree archive import/export code. It is hidden from GObject introspection.

## Important APIs and Control Flow
When `HAVE_LIBARCHIVE` is enabled, it defines autoptr cleanup aliases for `struct archive` readers/writers and `archive_entry`. `ot_archive_read_new()` allocates a reader, enables all filters or legacy compression support depending on libarchive feature macros, and enables all formats. `ot_open_archive_read(path, error)` and `ot_open_archive_read_fd(fd, error)` create readers and open them with an 8192-byte block size, mapping libarchive failures to `G_IO_ERROR_FAILED`.

## State, Dependencies, Integration, Risks, and Tests
State is owned by returned libarchive objects and cleaned by `archive_read_free()` or related cleanup functions. Dependencies include `config.h`, `otutil`, GIO, and libarchive headers behind feature guards. Integration points include archive import commands and `OstreeLibarchiveInputStream`. Risks are build-configuration drift, all-format/all-filter attack surface, and caller responsibility to handle archive entry iteration safely. Test signals should include opening by path and fd, unsupported/corrupt archives, feature-macro builds, and cleanup on early error.

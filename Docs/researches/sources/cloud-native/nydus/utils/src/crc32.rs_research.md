# sources/cloud-native/nydus/utils/src/crc32.rs

Purpose: CRC32 checksum helper using the iSCSI polynomial for buffers, readers, digesters, and raw fd ranges.

Important APIs/types/functions: `Algorithm::{None,Crc32Iscsi}` with display, default, and numeric conversions. `Crc32` wraps `crc::Crc<u32, Table<16>>`. Methods are `new`, `from_buf`, `from_reader`, `digester`, and `from_raw_fd`.

Control flow: `Crc32::new` selects `CRC_32_ISCSI`, with `Algorithm::None` currently falling back to the same implementation. `from_reader` streams through a 1 MiB buffer until EOF. `from_raw_fd` uses `nix::sys::uio::pread` from a starting offset for a requested size, retrying interrupted reads and stopping on EOF or requested byte count.

State and persistence: no persistent state. Digesters hold incremental checksum state.

Dependencies and integration points: depends on `crc`, `nix::sys::uio`, and project `last_error!` macro. Storage utilities use it for `check_crc`; other chunk verification paths can use it over memory, readers, or file descriptors.

Risks: `Algorithm::None` behaving as CRC32 may surprise callers expecting disabled checksum behavior. `from_raw_fd` silently returns checksum of fewer bytes if EOF occurs before `size`; callers must compare file size separately if short reads are invalid. Raw fd API does not own or close the fd.

Test signals: tests cover display/default/conversions, known checksum for `"123456789"`, empty buffers, large reader input, incremental digester, Linux memfd raw-fd checksum with offset and zero-size reads.

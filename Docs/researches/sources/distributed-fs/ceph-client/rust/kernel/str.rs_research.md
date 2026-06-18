## sources/distributed-fs/ceph-client/rust/kernel/str.rs

Purpose: provides byte-string, C-string extension, formatting-buffer, boolean-parsing, and owned C string utilities for Rust kernel code.

Important APIs/types/functions: `BStr` is a transparent unsized byte-string wrapper with `len`, `is_empty`, `from_bytes`, `strip_prefix`, display/debug escaping, indexing, and `b_str!`. `CStrExt` adds `from_char_ptr`, mutable unchecked construction, `as_char_ptr`, allocation into `CString`, and ASCII case conversion. `c_str!` builds static `CStr`s. `RawFormatter`, `Formatter`, and `NullTerminatedFormatter` support bounded raw formatting. `kstrtobool` and `kstrtobool_bytes` wrap kernel boolean parsing. `CString` owns a nul-terminated, interior-nul-free `KVec<u8>`.

Control flow: `CString::try_from_fmt` first formats into a counting `RawFormatter`, allocates exact capacity, formats again with bounds checking, increments vector length, then scans for interior nul with `memchr`. Boolean parsing passes either a C string pointer or a small stack nul-terminated byte array to `kstrtobool`.

State/persistence: owned state appears only in `CString`'s vector. Formatters track pointer positions or remaining buffer slices. No persistent storage.

Dependencies/integration: integrates with kernel allocation, `fmt`, C string literals, `bindings::kstrtobool`, `memchr`, and prelude `CStr`.

Risks: unchecked mutable CStr construction and `to_bytes_mut` rely on layout assumptions and caller-maintained nul invariants. `RawFormatter` can advance beyond the buffer by design, so callers must use `Formatter` when overflow is an error. `kstrtobool_bytes` intentionally considers only two input bytes. Formatting arbitrary bytes escapes non-printable/non-ASCII values rather than validating UTF-8.

Test signals: KUnit tests cover CStr UTF-8 conversion failure/success, CStr/BStr display/debug escaping for byte ranges, boolean parsing examples, and formatter behavior through `CString::try_from_fmt`.

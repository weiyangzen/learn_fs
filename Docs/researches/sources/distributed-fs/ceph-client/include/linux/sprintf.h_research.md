<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sprintf.h -->
# sources/distributed-fs/ceph-client/include/linux/sprintf.h

Purpose: Declares kernel formatted-printing and scanning APIs plus pointer hashing controls.

Important APIs/types/functions: `num_to_str()`, `sprintf()`, `vsprintf()`, `snprintf()`, `vsnprintf()`, `scnprintf()`, `vscnprintf()`, `kasprintf()`, `kvasprintf()`, `kvasprintf_const()`, `sscanf()`, `vsscanf()`, `no_hash_pointers`, `hash_pointers_finalize()`, and `rust_fmt_argument()`.

Control flow: The header supplies prototypes with `__printf`/`__scanf` compiler format checking. Implementations elsewhere format into caller buffers, allocate formatted strings, parse input strings, and handle `%p` pointer hashing policy.

State and persistence behavior: Formatting state is transient. `no_hash_pointers` and hash finalization affect global pointer-display policy.

Dependencies: Requires compiler attributes, kernel types, `stdarg.h`, GFP allocation types, and Rust formatting integration for `%pA`.

Integration points: Kernel logging, sysfs/proc/debugfs text generation, allocation formatting, and Rust-to-C formatting support.

Risks: `sprintf()` can overflow if callers do not size buffers; pointer formatting can leak addresses if hashing is disabled or not finalized correctly; format-string mismatches should be caught by attributes.

Test signals: Format compiler warnings, lib/vsprintf tests, pointer hashing tests, allocation-failure tests for `kasprintf`, and Rust `%pA` formatting tests where enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sprintf.h -->

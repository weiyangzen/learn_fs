## sources/distributed-fs/ceph-client/lib/tests/printf_kunit.c

### Purpose
This KUnit suite validates kernel `vsnprintf()`/`kvasprintf()` behavior and many kernel-specific `%p` formatting extensions. It checks output text, return lengths, null termination, truncation behavior, guard bytes around buffers, and formatted representations of kernel structures, addresses, flags, bitmaps, firmware nodes, FourCC values, and error pointers.

### Important APIs, types, and functions
`do_test()` is the core verifier: it fills a padded allocation with `FILL_CHAR`, calls `vsnprintf()`, checks the returned length, guard regions before and after the buffer, null termination, no writes beyond the terminator, and expected bytes. `__test()` runs each format through full-size, randomized truncated-size, zero-size, and `kvasprintf()` paths. The `test()` macro captures file/line. Cases include basic strings/numbers, pointer hashing (`hash_pointer()`, `plain_hash_to_buffer()`), null/error/invalid pointers, `struct resource`, `struct range`, hex strings, MAC, IPv4/IPv6, UUID, dentry path formatting, time/date formats, bitmaps, page/vma/gfp flags, firmware/software nodes, FourCC variants, and `%pe`.

### Control flow
`printf_suite_init()` allocates one padded test buffer and resets `total_tests`; `printf_suite_exit()` frees it and logs the total. Each test case calls the shared `test()` helper repeatedly. Pointer hashing tests may skip when pointer hashing is disabled or the CRNG has not initialized. `fwnode_pointer()` registers a small software-node group, validates full and short path output, then unregisters it.

### State and persistence
Persistent suite state is limited to `total_tests`, `test_buffer`, and `alloced_buffer`, all suite-scoped and freed at exit. Static `test_dentry[]` provides a synthetic dentry tree. Software nodes are registered only for the duration of `fwnode_pointer()`.

### Dependencies and integration points
The suite depends on KUnit, kernel formatting internals, random truncation, resource/range/socket/IP/UUID/dcache/time/bitmap/mm/property helpers, and global pointer-hashing behavior (`no_hash_pointers`). It integrates as suite name `printf`.

### Risks and edge cases
Several registered cases are empty placeholders (`symbol_ptr`, `kernel_ptr`, `addr`, `escaped_str`, `struct_va_format`, `struct_clk`, `netdev_features`), so suite coverage is broad but not complete for those format classes. Pointer hash expectations depend on runtime security settings and CRNG readiness, causing skips. Random truncation size broadens coverage but can make a particular truncation failure less deterministic.

### Test signals
High-value signals are guard-byte checks for buffer safety, cross-checking `vsnprintf()` and `kvasprintf()`, explicit hashed-pointer handling, structured `%p` format expected strings, flag-name fallback to numeric output, and suite total logging.

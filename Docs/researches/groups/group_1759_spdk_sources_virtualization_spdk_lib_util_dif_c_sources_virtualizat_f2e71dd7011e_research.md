# Group Research: group_1759_spdk_sources_virtualization_spdk_lib_util_dif_c_sources_virtualizat_f2e71dd7011e

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/dif.c -->
# File Research: sources/virtualization/spdk/lib/util/dif.c

This file implements SPDK DIF/DIX protection information utilities. It supports 16-bit, 32-bit, and 64-bit PI formats; DIF types 1, 2, and 3; interleaved metadata; separate metadata buffers; streaming partial-block generation/verification; protection-information copy insertion/stripping; error injection; CRC32C update; and reference-tag remapping.

The file defines the private `struct spdk_dif` layouts for the three PI formats and a private `_dif_sgl` iterator used to walk or construct iovec arrays. The SGL helpers advance across fragmented iovecs, validate total length, test block-size alignment, append split ranges, and copy iterator state. Most public operations choose a fast whole-block path when every iovec length is a multiple of the relevant block size, and fall back to split helpers when a logical block crosses iovec boundaries.

`spdk_dif_ctx_init()` validates PI format, DIF type, metadata size, interleaved metadata geometry, and data-block alignment requirements. It computes `guard_interval`, reference-tag offset, initial guard seed, and remapped reference-tag state. `spdk_dif_ctx_set_data_offset()` and `spdk_dif_ctx_set_remapped_init_ref_tag()` update stream/reference mapping fields after initialization.

The guard path maps PI format to CRC algorithm: T10 DIF CRC16 for PI16, NVMe CRC32C for PI32, and NVMe CRC64 for PI64. `_dif_generate()` writes guard, application tag, and reference tag fields depending on enabled DIF flags. `_dif_verify()` checks guard, application tag mask, and reference tag, honoring ignore rules: type 1/2 ignore all checks when application tag is `0xffff`; type 3 ignores when application tag and reference tag are both ignore values.

The main DIF APIs are `spdk_dif_generate()`, `spdk_dif_verify()`, and `spdk_dif_update_crc32c()`. They operate on buffers where metadata is part of each block. Split variants carry guard state across fragmented block pieces and copy DIF bytes through a temporary `struct spdk_dif` when the DIF field itself crosses iovec boundaries.

The copy helpers cover host/device metadata conversion. `spdk_dif_generate_copy()` either inserts DIF into a bounce buffer when PRACT is not set or metadata size equals DIF size, or overwrites existing metadata while regenerating DIF. `spdk_dif_verify_copy()` either strips DIF into data-only iovs while verifying or verifies/copies full blocks depending on PRACT and metadata size. Disabled-DIF variants copy data while skipping or preserving metadata slots without checking PI fields.

DIX support handles data and metadata as separate iovecs. `spdk_dix_generate()` writes PI into the metadata iov, `spdk_dix_verify()` validates separate metadata, and `spdk_dix_inject_error()` can flip bits in metadata guard/application/reference fields or in data. DIX metadata is represented as a single iovec in the public API.

`spdk_dif_inject_error()` and `spdk_dix_inject_error()` randomly choose a block, byte range, and bit, then flip a bit in the requested PI/data field. The code reseeds `rand()` with `time(0)` per injection call, so repeated calls in the same second may not be statistically independent.

The streaming APIs support partial ranges over metadata-interleaved buffers. `spdk_dif_set_md_interleave_iovs()` maps a data range to iovecs that skip metadata holes. `spdk_dif_generate_stream()`, `spdk_dif_verify_stream()`, and `spdk_dif_update_crc32c_stream()` compute the full buffer range containing data plus metadata, process block fragments, and preserve `ctx->last_guard` across calls. `spdk_dif_get_range_with_md()` and `spdk_dif_get_length_with_md()` convert data-only offsets/lengths to metadata-inclusive ranges.

Reference-tag remapping is implemented for DIF and DIX through `spdk_dif_remap_ref_tag()` and `spdk_dix_remap_ref_tag()`. These optionally verify the existing reference tag, then rewrite it using `ctx->remapped_init_ref_tag`, preserving ignore semantics and DIF-disabled shortcuts.

Important invariants are geometry correctness, guard interval calculation, PI-format field offsets, endian conversion, reference-tag masks, SGL length validation before iteration, and preserving guard state for split/streaming operations. Changes here affect NVMe DIF/DIX data integrity paths directly.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/dif.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/fd.c -->
# File Research: sources/virtualization/spdk/lib/util/fd.c

This file provides small file-descriptor utilities for device geometry, file size, and nonblocking mode.

`spdk_fd_get_blocklen()` queries sector/block length with platform-specific ioctls: FreeBSD `DIOCGSECTORSIZE`, `DKIOCGETBLOCKSIZE` where available, or Linux `BLKSSZGET`. It returns zero when no supported query succeeds.

`spdk_fd_get_size()` uses `fstat()` to reject symlinks, return regular-file size, and query block/character device size via `dev_get_size()`. Device size uses FreeBSD `DIOCGMEDIASIZE` or Linux `BLKGETSIZE64`; unsupported or failed cases return zero.

`spdk_fd_set_nonblock()` and `spdk_fd_clear_nonblock()` share `fd_update_nonblock()`, which reads `F_GETFL`, updates `O_NONBLOCK` only when needed, and writes `F_SETFL`. Errors are logged with `spdk_strerror()` and returned as negative errno.

The main dependency is POSIX file status and fcntl/ioctl behavior. Callers must treat zero size/block length as “unknown or unsupported,” not necessarily a valid zero-length device.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/fd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/fd_group.c -->
# File Research: sources/virtualization/spdk/lib/util/fd_group.c

This file implements SPDK fd groups on Linux using epoll, plus `-ENOTSUP` stubs for non-Linux builds. An fd group owns event handlers, can be nested under another group, can wrap callback execution, and can expose the current epoll event through thread-local storage.

The Linux implementation stores each registered fd in an `event_handler` with callback, callback argument, fd, epoll event mask, fd type, owner group, name, and a state machine: waiting, running, or removed. Removed handlers are freed immediately unless they are currently in a wait loop, in which case free is deferred until the loop notices `EVENT_HANDLER_STATE_REMOVED`.

`spdk_fd_group_create()` allocates a group and epoll fd. `spdk_fd_group_destroy()` asserts the group has no registered fds, no parent, and no children before closing the epoll fd. `spdk_fd_group_add()`, `spdk_fd_group_add_for_events()`, and `spdk_fd_group_add_ext()` allocate handlers and add them to the root epoll instance. Extended opts use an ABI-size-aware copy pattern for event mask and fd type. `spdk_fd_group_remove()` deletes the fd from the root epoll instance and removes the handler from the owner list.

Nested groups are handled by hoisting child fds into the root epoll fd. `spdk_fd_group_nest()` rejects children that already have parents and parents with wrapper functions, then migrates all child fds from the child epoll fd to the parent root. `spdk_fd_group_unnest()` migrates fds back to the child epoll fd and removes the child link. Migration helpers include recovery paths for partial epoll add/delete failures, returning `-ENOTRECOVERABLE` when state may not be restored.

`spdk_fd_group_wait()` only works on root groups. It calls `epoll_wait()`, marks returned handlers running, optionally drains eventfd counters for `SPDK_FD_TYPE_EVENTFD`, then invokes callbacks directly or through the owner group’s wrapper function. It stores the active epoll event in thread-local `g_event` so `spdk_fd_group_get_epoll_event()` can return it during callback execution.

`spdk_fd_group_event_modify()` updates a registered fd’s event mask with `EPOLL_CTL_MOD`. `spdk_fd_group_set_wrapper()` installs one callback wrapper per group and rejects wrapping groups with children.

Key invariants are root ownership of active epoll registrations, accurate `num_fds` accounting, no blocking wait on nested groups, deferred handler free during callbacks, and no wrapper on a group with nested children.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/fd_group.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/file.c -->
# File Research: sources/virtualization/spdk/lib/util/file.c

This file implements whole-file loading and sysfs attribute readers.

`spdk_posix_file_load()` reads a `FILE *` into a reallocating heap buffer, starting at 128 KiB and doubling up to 1 GiB. It returns the buffer and sets the final byte count on EOF, or frees and returns null on allocation/read error or if the file exceeds the growth cap.

`spdk_posix_file_load_from_name()` opens a file by name, delegates to `spdk_posix_file_load()`, closes the file, and returns the allocated contents.

`read_sysfs_attribute()` formats a path with `spdk_vsprintf_alloc()`, opens it, reads one line with `getline()`, strips a trailing newline, and returns the allocated string through `attribute_p`. `spdk_read_sysfs_attribute()` is the varargs wrapper. `spdk_read_sysfs_attribute_uint32()` reads a string attribute, parses it with `spdk_strtoll()`, checks the value is in `uint32_t` range, and returns the integer.

Memory ownership is caller-facing: successful file loads and sysfs reads return heap buffers that callers must free. Errors are negative errno where possible.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/file.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/hexlify.c -->
# File Research: sources/virtualization/spdk/lib/util/hexlify.c

This file converts binary data to lowercase hexadecimal strings and back.

`spdk_hexlify()` allocates a `len * 2 + 1` output string, converts each input byte through a nibble-to-character helper, and null-terminates the result. The generated alphabet is lowercase `0123456789abcdef`.

`spdk_unhexlify()` requires an even-length hex string, allocates `len / 2` bytes, accepts uppercase and lowercase hex digits, and returns null on odd length, invalid character, or allocation failure. Invalid input is logged.

The unhexlify result is raw binary and is not null-terminated beyond its allocated byte count; callers need to know the expected decoded length from the input string length.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/hexlify.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/iov.c -->
# File Research: sources/virtualization/spdk/lib/util/iov.c

This file provides generic iovec memory operations and iterators.

`spdk_iov_memset()` fills all iovec buffers. `spdk_ioviter_first()` and `spdk_ioviter_firstv()` initialize two-way or N-way iterators. `spdk_ioviter_next()` and `spdk_ioviter_nextv()` return the next aligned span length across all tracked iovec lists, advancing each list by the minimum remaining segment size. Iteration stops when any stream is exhausted.

`spdk_iovcpy()` and `spdk_iovmove()` copy or memmove between source and destination iovec arrays using the two-way iterator, returning the total transferred bytes.

`spdk_iov_xfer_init()` initializes a one-way transfer cursor. `spdk_iov_xfer_from_buf()` copies from a flat buffer into iovecs, while `spdk_iov_xfer_to_buf()` copies from iovecs into a flat buffer. `spdk_copy_iovs_to_buf()` and `spdk_copy_buf_to_iovs()` are convenience wrappers.

The iterators assume nonempty iovec arrays when initialized and do not perform deep validation of null bases or invalid counts. The transfer cursor preserves position across calls, making it useful for incremental protocol marshalling.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/iov.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/math.c -->
# File Research: sources/virtualization/spdk/lib/util/math.c

This file implements integer floor-log2 helpers.

`spdk_u32log2()` returns `31 - __builtin_clz(x)` for nonzero 32-bit values, and returns zero for input zero because log zero is undefined. `spdk_u64log2()` does the same for 64-bit values using `__builtin_clzll()`.

On GCC 6+ x86 ELF non-Clang builds, both functions use `target_clones("bmi", "arch=core2", "arch=atom", "default")` so GCC can emit multiple architecture-specific implementations.

The functions rely on static assertions that `uint32_t` matches `unsigned int` and `uint64_t` matches `unsigned long long` for the selected builtins.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/math.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/md5.c -->
# File Research: sources/virtualization/spdk/lib/util/md5.c

This file wraps OpenSSL EVP MD5 operations behind SPDK’s `spdk_md5ctx`.

`spdk_md5init()` validates the context, allocates an `EVP_MD_CTX`, initializes it for `EVP_md5()`, and destroys the context on initialization failure. `spdk_md5update()` ignores null data or zero length as a successful no-op, otherwise delegates to `EVP_DigestUpdate()`. `spdk_md5final()` finalizes into the caller-provided digest buffer, destroys the EVP context, and clears the stored pointer.

Return conventions mix SPDK-style `-1` validation failures with OpenSSL’s `1` success / `0` failure for update/final calls. Callers need to treat nonpositive values carefully.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/md5.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/net.c -->
# File Research: sources/virtualization/spdk/lib/util/net.c

This file implements small network address helpers.

`spdk_net_get_interface_name()` scans `getifaddrs()` for an up IPv4 interface whose address string matches the supplied IP, then copies the interface name. It returns `-ENODEV` if none match and `-ENOMEM` if the name does not fit.

`spdk_net_get_address_string()` converts `AF_INET` or `AF_INET6` sockaddr addresses to text through `inet_ntop()`. Unsupported families or `inet_ntop()` failures return negative errno.

`spdk_net_is_loopback()` gets the local socket address, finds the matching active interface, queries `SIOCGIFFLAGS`, and returns whether `IFF_LOOPBACK` is set. Failures return false.

`spdk_net_getaddr()` fills optional local address/port and peer address/port for a socket. It accepts Unix sockets as addressless, rejects unsupported families, rejects peer requests on listening sockets, and uses `getsockname()`, `getsockopt(SO_ACCEPTCONN)`, and `getpeername()` for TCP-style sockets.

`spdk_net_compare_address()` parses two IPv4 or IPv6 strings with `inet_pton()` and returns `memcmp()` ordering through `cmp`. It validates null arguments and address family, returning `-EAFNOSUPPORT` for unsupported families.

Important behavior is that several helpers log but return generic negative errno, and `spdk_net_is_loopback()` intentionally collapses all errors to false.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/net.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/pipe.c -->
# File Research: sources/virtualization/spdk/lib/util/pipe.c

This file implements a single-buffer circular pipe with iovec-based reader/writer access and optional shared buffer grouping.

`spdk_pipe_create()` wraps a caller-provided buffer and size in a pipe object. `spdk_pipe_destroy()` removes the pipe from any group, returns the underlying buffer pointer, and frees the pipe object.

Writer APIs expose writable space without copying. `spdk_pipe_writer_get_buffer()` returns up to two iovecs for the current free range, wrapping at the end of the buffer when needed. If the pipe is full or the request is zero, it returns an empty first iovec. `spdk_pipe_writer_advance()` validates the requested advance fits in free space, moves the write pointer, wraps if needed, and marks the pipe full when write catches read.

Reader APIs mirror this. `spdk_pipe_reader_bytes_available()` computes readable bytes. `spdk_pipe_reader_get_buffer()` returns up to two readable iovecs. `spdk_pipe_reader_advance()` validates the read advance, clears `full`, resets both pointers to zero when empty, and, if the pipe belongs to a group, returns its buffer to the group and sets `pipe->buf` null.

Pipe groups let empty pipes share buffers of matching size. `spdk_pipe_group_create()` and destroy manage a list of free buffers. `spdk_pipe_group_add()` associates a pipe with a group and immediately releases its buffer if the pipe is empty. `spdk_pipe_group_remove()` reacquires a matching buffer before disassociating the pipe.

The implementation assumes single-threaded or externally synchronized access. Group buffers are stored by casting the start of the pipe buffer to `struct spdk_pipe_buf`, so grouped buffers must be large/aligned enough to hold that header when idle.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/strerror_tls.c -->
# File Research: sources/virtualization/spdk/lib/util/strerror_tls.c

This file provides `spdk_strerror()`, a thread-local strerror wrapper.

It declares a `static __thread char strerror_message[64]`, calls `spdk_strerror_r()` into that buffer, and returns the thread-local pointer. The result is overwritten by the next `spdk_strerror()` call on the same thread.

This is a convenience layer over `string.c`’s portable `spdk_strerror_r()` implementation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/strerror_tls.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/string.c -->
# File Research: sources/virtualization/spdk/lib/util/string.c

This file contains SPDK string allocation, parsing, trimming, numeric conversion, and string-array helpers.

Formatted allocation helpers include `spdk_vsprintf_append_realloc()`, `spdk_sprintf_append_realloc()`, `spdk_vsprintf_alloc()`, and `spdk_sprintf_alloc()`. They use `vsnprintf(NULL, 0, ...)` to size output, reallocate the existing buffer when appending, and return null on formatting or allocation failure.

Basic string utilities include `spdk_strlwr()` for in-place lowercase, `spdk_str_trim()` for in-place leading/trailing whitespace removal, `spdk_str_chomp()` for removing trailing CR/LF, `spdk_strcpy_pad()` and `spdk_strlen_pad()` for fixed-size padded strings, and `spdk_mem_all_zero()` for byte-wise zero testing.

`spdk_strsepq()` is a quoted tokenizer. It splits on delimiter characters while honoring single quotes, double quotes, and backslash escapes, removes quote characters, compacts escaped characters in place, skips trailing delimiters, and advances `stringp`.

`spdk_parse_ip_addr()` destructively parses either `host:port` IPv4-style strings or `[ipv6]:port` strings, replacing separators with null bytes and returning host and optional port pointers.

`spdk_strerror_r()` handles GNU and POSIX `strerror_r()` variants and formats `Unknown error N` on failure. `spdk_parse_capacity()` parses unsigned integer capacities with optional binary suffix K/M/G and reports whether a suffix was present.

`spdk_strtol()` and `spdk_strtoll()` wrap libc conversions but reject trailing non-integer characters, overflow, other errno failures, and negative values. They return negative errno-style values on invalid input, so callers cannot parse negative numbers through these helpers.

String-array helpers allocate, duplicate, and free null-terminated `char **` arrays. `spdk_strarray_from_string()` splits on any delimiter character using `strpbrk()` and preserves empty fields between adjacent delimiters. `spdk_strarray_dup()` deep-copies a null-terminated string array. `spdk_strarray_free()` releases all entries and the array itself.

`spdk_strcpy_replace()` copies `src` to `dst` while replacing all occurrences of `search` with `replace`, after precomputing required output size. It returns `-EINVAL` for null arguments or insufficient destination space.

Important caveats are destructive parsing in `spdk_parse_ip_addr()` and `spdk_strsepq()`, unsigned-only numeric wrappers, and caller ownership of allocated format/string-array results.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/string.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/util_internal.h -->
# File Research: sources/virtualization/spdk/lib/util/util_internal.h

This private utility header declares shared CRC32 internals.

It defines reflected polynomial constants for IEEE CRC-32 and CRC-32C Castagnoli, defines `struct spdk_crc32_table` with 256 table entries, and declares `crc32_table_init()` and `crc32_update()`.

The header is intentionally internal to `lib/util` CRC implementations. Consumers provide an initialized table and previous CRC value to update partial checksums.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/util_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/uuid.c -->
# File Research: sources/virtualization/spdk/lib/util/uuid.c

This file wraps platform UUID handling and implements UUIDv5/SHA1 generation fallback.

When `SPDK_CONFIG_HAVE_LIBUUID` is available, it statically asserts `struct spdk_uuid` matches `uuid_t` and delegates parse, lower-case format, compare, generate, copy, null test, and null set to libuuid.

On FreeBSD, it uses `<uuid.h>` equivalents. The parse wrapper rejects empty strings explicitly to match Linux libuuid behavior. Formatting uses `uuid_to_string()`, copies into the caller buffer, and frees the library-allocated string.

`spdk_uuid_generate_sha1()` uses `uuid_generate_sha1()` when configured. Otherwise it computes SHA1 over namespace UUID bytes plus the supplied name using OpenSSL EVP, copies the first 16 digest bytes into the UUID, and sets version 5 and RFC4122 variant bits in raw bytes 6 and 8.

The main invariants are buffer size `SPDK_UUID_STRING_LEN`, cross-platform behavior consistency for empty strings, and correct version/variant bit setting for SHA1-generated UUIDs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/xor.c -->
# File Research: sources/virtualization/spdk/lib/util/xor.c

This file implements XOR parity generation across multiple source buffers.

`spdk_xor_gen()` validates source count `2 <= n <= 256`, then delegates to an optimized or basic implementation. The basic path uses 64-bit word XOR when destination and all sources are aligned to `sizeof(uint64_t)`, and byte-wise XOR otherwise. Any tail bytes after the word-aligned portion are processed byte-wise.

When SPDK is built with ISA-L, `do_xor_gen()` uses ISA-L `xor_gen()` when all buffers meet 32-byte alignment; otherwise it falls back to the basic implementation. `spdk_xor_get_optimal_alignment()` returns 32 with ISA-L or `sizeof(uint64_t)` without it.

Important constraints are the maximum source count of 256, alignment-sensitive acceleration, and caller responsibility for valid non-overlapping or otherwise safe buffers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/xor.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/util/zipf.c -->
# File Research: sources/virtualization/spdk/lib/util/zipf.c

This file implements a Zipf-distributed integer generator.

`spdk_zipf_create()` allocates generator state, stores range and theta, computes alpha, zeta over the range, eta, and a limit for returning value 1. The zeta calculation sums exactly for up to 10 million entries and approximates larger tails in 1 million-entry chunks using averaged increments.

`spdk_zipf_generate()` draws a uniform random value with `spdk_rand_xorshift64()`, scales it by `zetan`, returns 0 or 1 for the first two regions, or computes the general Zipf value and wraps it by `range`. `spdk_zipf_free()` frees and nulls the caller’s pointer.

A notable behavior is that `spdk_zipf_create(uint64_t range, double theta, uint32_t seed)` ignores the supplied `seed` parameter and instead initializes `zipf->seed` from `spdk_rand_xorshift64_seed()`. Also, the code assumes sensible nonzero range and theta values; it does not validate them.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/util/zipf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/Makefile -->
# File Research: sources/virtualization/spdk/lib/vfio_user/Makefile

This Makefile is the top-level build glue for SPDK’s `lib/vfio_user` subtree.

It sets `SPDK_ROOT_DIR` to two directories above the current directory, includes `mk/spdk.common.mk`, declares `DIRS-y += host`, and makes `all` and `clean` recurse into that subdirectory through `mk/spdk.subdirs.mk`.

The file does not build sources directly; it delegates the library build to `lib/vfio_user/host/Makefile`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/host/Makefile -->
# File Research: sources/virtualization/spdk/lib/vfio_user/host/Makefile

This Makefile builds the SPDK vfio-user host library.

It sets `SPDK_ROOT_DIR` to three directories above the current directory, includes common SPDK make settings, sets shared library version `SO_VER := 7` and `SO_MINOR := 0`, builds `vfio_user_pci.c` and `vfio_user.c`, names the library `vfio_user`, and points `SPDK_MAP_FILE` at `spdk_vfio_user.map`.

The file finishes by including `mk/spdk.lib.mk`, so normal SPDK library rules own compilation, linking, and install metadata.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/host/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/host/vfio_user.c -->
# File Research: sources/virtualization/spdk/lib/vfio_user/host/vfio_user.c

This file implements the client-side vfio-user socket protocol used by SPDK’s vfio-user PCI host wrapper.

`vfio_user_write()` sends a vfio-user header plus payload over a Unix socket with optional file descriptors through `SCM_RIGHTS`. It retries `sendmsg()` on `EINTR`, uses `MSG_NOSIGNAL`, and asserts the fd count fits `VFIO_MAXIMUM_SPARSE_MMAP_REGIONS`.

`read_fd_message()` receives the fixed header and any ancillary file descriptors with `recvmsg()`, rejects truncated control/data messages, and copies received fds into the request object. `vfio_user_read()` reads the header first, checks vfio-user error flags, then reads any remaining payload bytes with `read()`.

`vfio_user_dev_send_request()` is the central request/response helper. It builds a `vfio_user_request`, copies an argument payload up to 4096 bytes, sends DMA map/unmap requests with fds when supplied, waits for a mandatory reply, validates reply payload size, copies response payload back into the caller buffer for non-DMA-map requests, and returns any received fds for region-info replies.

`vfio_user_check_version()` negotiates vfio-user version 0.1. `vfio_user_get_dev_region_info()` and `vfio_user_get_dev_info()` issue device info queries. `vfio_user_dev_dma_map_unmap()` sends DMA map/unmap messages using the SPDK memory region’s IOVA, size, file offset, and fd. `vfio_user_dev_mmio_access()` allocates a variable-length region access message for region reads/writes and copies read data back.

`vfio_user_dev_setup()` opens an `AF_UNIX` stream socket, sets `FD_CLOEXEC`, validates the socket path length, connects to `dev->path`, stores the fd, and verifies protocol version.

Important invariants are the fixed maximum payload size, fd-passing limits, one request followed by one mandatory reply, and correct distinction between DMA requests that send fds and query requests that receive fds.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/host/vfio_user.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/host/vfio_user_internal.h -->
# File Research: sources/virtualization/spdk/lib/vfio_user/host/vfio_user_internal.h

This private header defines shared vfio-user host structures and internal function declarations.

It sets vfio-user protocol version constants to major 0, minor 1. It defines maximum memory regions as 16 and maximum sparse mmap regions per BAR as 8.

`struct vfio_memory_region` tracks IOVA, size, virtual address, mmap offset, fd, and list linkage for DMA mappings. `struct vfio_sparse_mmaps` records one mapped sparse BAR range. `struct vfio_pci_region` stores BAR offset, size, flags, sparse mmap count, and sparse mmap entries. `struct vfio_device` stores socket fd, generated name, socket path, PCI region array, flags, SPDK memory map, and the DMA memory-region list.

The declarations connect `vfio_user.c` protocol helpers with `vfio_user_pci.c` PCI setup: device setup, device/region info queries, DMA map/unmap, MMIO access, and a fuzzing-only raw request sender.

The header is Linux-specific through `<linux/vfio.h>` and vfio-user protocol structures.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/host/vfio_user_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/host/vfio_user_pci.c -->
# File Research: sources/virtualization/spdk/lib/vfio_user/host/vfio_user_pci.c

This file implements SPDK’s vfio-user PCI host wrapper. It connects to a vfio-user device, maps PCI BAR/config regions, registers SPDK memory for DMA with the remote device, and exposes BAR access helpers.

`spdk_vfio_user_pci_bar_access()` validates a BAR offset/length, performs direct memcpy when the range is inside a mapped sparse mmap region, and falls back to vfio-user region read/write messages when the region is not mmapped. `spdk_vfio_user_get_bar_addr()` returns a direct pointer only if the requested range is inside an mmapped BAR region.

DMA memory tracking uses a TAILQ of `vfio_memory_region`. `vfio_mr_map_notify()` is registered as an SPDK memory-map callback. On unregister, it finds the region, sends vfio-user DMA unmap, removes it from the list, and frees it. On register, it obtains the memory fd and offset with `spdk_mem_get_fd_and_offset()`, records vaddr as IOVA, adds the region, and sends vfio-user DMA map with the fd.

`vfio_device_get_info_cap()` walks a `vfio_region_info` capability chain. `vfio_device_setup_sparse_mmaps()` parses `VFIO_REGION_INFO_CAP_SPARSE_MMAP`, stores sparse ranges, mmaps each supplied fd when present, closes all fds, and records the sparse mmap count. `vfio_device_map_region()` mmaps a whole BAR when sparse mmap setup is unavailable or fails.

`vfio_device_map_bars_and_config_region()` queries each reported PCI region with `VFIO_USER_DEVICE_GET_REGION_INFO`, stores size/offset/flags, and maps regions that advertise `VFIO_REGION_INFO_FLAG_MMAP`. `vfio_device_unmap_bars()` unmaps all mapped regions and clears region state.

`spdk_vfio_user_setup()` allocates a device, initializes the memory-region list, assigns path and generated name, connects and negotiates vfio-user, queries device info, maps BAR/config regions, allocates the SPDK memory map for DMA notifications, and returns the device. `spdk_vfio_user_release()` unmaps BARs, frees the memory map, closes the socket, and frees the device. `spdk_vfio_user_dev_send_request()` exposes the raw request helper for fuzzing.

Important invariants are fd ownership after region queries, mmap lifetime matching release, maximum memory-region limits, and SPDK memory registration callbacks staying consistent with remote DMA mappings.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vfio_user/host/vfio_user_pci.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vfu_tgt/Makefile -->
# File Research: sources/virtualization/spdk/lib/vfu_tgt/Makefile

This Makefile builds SPDK’s libvfio-user target library.

It sets shared library version `SO_VER := 5` and `SO_MINOR := 0`, builds `tgt_endpoint.c` and `tgt_rpc.c`, includes libvfio-user headers through `VFIO_USER_INCLUDE_DIR`, links against `VFIO_USER_LIBRARY_DIR`, and adds system libraries `-lvfio-user -ljson-c`.

The output library is `vfu_tgt`, with exported symbols controlled by `spdk_vfu_tgt.map`, and compilation uses standard `mk/spdk.lib.mk` rules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vfu_tgt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vfu_tgt/tgt_endpoint.c -->
# File Research: sources/virtualization/spdk/lib/vfu_tgt/tgt_endpoint.c

This file implements SPDK’s libvfio-user target endpoint manager. It registers endpoint device-type operations, creates vfio-user PCI endpoints, realizes PCI configuration and regions, attaches clients, handles DMA memory callbacks, and performs asynchronous endpoint shutdown on SPDK threads.

Global state includes the allowed target core mask, a mutex-protected endpoint list, a mutex-protected registered PCI device-ops list, the endpoint socket base path, and fini bookkeeping. `spdk_vfu_register_endpoint_ops()` installs one named `spdk_vfu_endpoint_ops` implementation, rejecting duplicates. `spdk_vfu_set_socket_path()` stores a base path and ensures it ends in `/`. `spdk_vfu_get_endpoint_by_name()` looks up live endpoints by name.

Each endpoint has an accept poller and a libvfio-user context poller. `tgt_accept_poller()` calls nonblocking `vfu_attach_ctx()` until a client connects, then calls the backend `attach_device()` hook and starts `tgt_vfu_ctx_poller()`. The context poller calls `vfu_run_ctx()` and handles `ENOTCONN` by unregistering itself, calling `detach_device()`, and marking the endpoint detached.

`tgt_endpoint_realize()` is the main construction path. It gets backend PCI device info, creates a libvfio-user socket context, configures logging, initializes PCIe config space, sets PCI IDs/class, adds vendor capabilities, adds PM/PCIe/MSI-X capabilities, configures each PCI region including sparse mmap descriptions and access callbacks, installs DMA add/remove callbacks, optional reset/quiesce callbacks, INTx/MSI-X irq counts, realizes the context, retrieves config-space and MSI-X capability pointers, and initializes selected config fields.

DMA callbacks register or unregister guest memory with SPDK only when the mapping is 2 MiB-aligned and read/write. Backend hooks `post_memory_add()` and `pre_memory_remove()` are called around SPDK memory registration/unregistration.

`vfu_parse_core_mask()` validates a requested endpoint cpumask is inside the global SPDK environment core mask and nonempty. `spdk_vfu_create_endpoint()` validates the endpoint name, rejects duplicates, finds a registered device type, builds the socket path, allocates and initializes endpoint private state through backend `init()`, realizes the endpoint, creates an SPDK thread, inserts the endpoint unless fini has started, and sends a message to start the accept poller on the endpoint thread.

Shutdown is asynchronous. `spdk_vfu_delete_endpoint()` removes the endpoint from the global list and sends `tgt_endpoint_thread_exit()` to its thread. That unregisters pollers, detaches the backend, destroys the libvfio-user context, then repeatedly calls backend `destruct()` until it no longer returns `-EAGAIN`. During global `spdk_vfu_fini()`, registered ops are freed, all endpoints are removed and asked to exit, and the fini callback runs after the last endpoint completes.

Accessor APIs expose endpoint id, name, libvfio-user context, private backend context, MSI-X/INTx state, PCI config pointer, and DMA map/unmap helpers. `spdk_vfu_map_one()` maps one guest address through `vfu_addr_to_sgl()` and `vfu_sgl_get()`, while `spdk_vfu_unmap_sg()` releases SGL mappings.

Key invariants are endpoint-list mutex protection, no endpoint creation after fini starts, backend hook ordering, libvfio-user context lifetime bound to endpoint thread shutdown, and 2 MiB alignment requirements before registering DMA memory with SPDK.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vfu_tgt/tgt_endpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vfu_tgt/tgt_internal.h -->
# File Research: sources/virtualization/spdk/lib/vfu_tgt/tgt_internal.h

This private header defines `struct spdk_vfu_endpoint`.

An endpoint stores its name, socket UUID/path, backend operation table, libvfio-user context, backend private context, accept and context pollers, attached state, MSI-X capability pointer, PCI config-space pointer, owning SPDK thread, and list linkage.

The structure is shared by endpoint management and RPC/backend integration. Its fields encode the endpoint lifetime model: one libvfio-user context, one SPDK thread, pollers on that thread, and backend private state controlled through `spdk_vfu_endpoint_ops`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vfu_tgt/tgt_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vfu_tgt/tgt_rpc.c -->
# File Research: sources/virtualization/spdk/lib/vfu_tgt/tgt_rpc.c

This file registers the `vfu_tgt_set_base_path` JSON-RPC method.

The RPC decoder expects a `path` string into an autogenerated `rpc_vfu_tgt_set_base_path_ctx`. `rpc_vfu_tgt_set_base_path()` decodes parameters, calls `spdk_vfu_set_socket_path()`, frees decoded request data, and returns boolean true on success. Decode or validation failures return `SPDK_JSONRPC_ERROR_INVALID_PARAMS` with `spdk_strerror(-rc)`.

The RPC is registered for runtime use with `SPDK_RPC_REGISTER("vfu_tgt_set_base_path", ...)`. Its only effect is changing the base directory used for future vfio-user endpoint socket paths.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vfu_tgt/tgt_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vhost/Makefile -->
# File Research: sources/virtualization/spdk/lib/vhost/Makefile

This Makefile builds SPDK’s vhost library.

It sets shared library version `SO_VER := 10` and `SO_MINOR := 0`, adds the current directory and environment C flags, builds `vhost.c`, `vhost_rpc.c`, `vhost_scsi.c`, `vhost_blk.c`, and `rte_vhost_user.c`, names the library `vhost`, and uses `spdk_vhost.map` as the map file.

The file delegates actual build mechanics to `mk/spdk.lib.mk`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vhost/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vhost/rte_vhost_user.c -->
# File Research: sources/virtualization/spdk/lib/vhost/rte_vhost_user.c

This file adapts DPDK vhost-user to SPDK vhost sessions. It owns guest physical address translation, split and packed virtqueue traversal, used-ring updates, interrupt/coalescing behavior, VM memory registration, session lifecycle, vhost-user message hooks, Unix socket registration, and shutdown coordination.

Address translation uses `rte_vhost_va_from_guest_pa()`. `vhost_gpa_to_vva()` requires the entire requested range to translate. Descriptor-to-iovec helpers split guest physical ranges into host iovecs and enforce `SPDK_VHOST_IOVS_MAX`.

Split-ring helpers read available ring entries, handle indirect descriptor tables, walk descriptor chains, log dirty pages when `VHOST_F_LOG_ALL` is negotiated, enqueue used-ring entries, update inflight tracking, and signal used vrings. Packed-ring helpers detect indirect descriptors, walk descriptor lists, restore/wrap avail and used indices, enqueue used packed descriptors, manage packed ring phase bits, and clear inflight descriptors.

Interrupt signaling is handled by `vhost_session_vq_used_signal()`. Without coalescing, it checks event suppression flags and calls DPDK’s nonblocking vring call when available. With coalescing, it updates per-queue request counters and delays interrupts based on configured delay and IOPS threshold. In interrupt mode, available-ring reads drain kickfds and may re-kick if unprocessed requests remain.

VM memory handling registers guest memory with SPDK for vtophys translation. `vhost_session_mem_register()` rounds mmap ranges to 2 MiB boundaries and skips duplicate starts; unregister mirrors that. `vhost_register_memtable_if_required()` fetches the DPDK memory table, detects changes against the current table, unregisters old memory, registers new memory, or frees unchanged tables.

Session lifecycle starts in `new_connection()`, which maps DPDK `vid` to a controller name, allocates a cache-line-aligned `spdk_vhost_session` plus backend session context, initializes semaphore/state, inserts it into the device session list, and installs DPDK extern message hooks. `start_device()` schedules backend `start_session()` on the vhost device thread after memory is present. `_stop_session()` waits for backend stop, saves vring bases, and clears queue state. `destroy_connection()` stops if needed, unregisters memory, removes the session, and frees it.

`enable_device_vq()` initializes one virtqueue from DPDK state, restores vring base and packed inflight state, allocates backend queue tasks, configures notification suppression according to interrupt mode, optionally calls backend `enable_vq()`, and updates session queue count. `set_device_vq_callfd()` forces an interrupt after migration/restart by incrementing used request count.

The DPDK callback table maps new/destroy device events to SPDK start/stop and new/destroy connection events to session allocation/free. Extern pre-message hooks stop running sessions before `GET_VRING_BASE` or memory-table replacement and delegate GET/SET_CONFIG to backend callbacks. Post-message hooks record negotiated features, initialize queues on `SET_VRING_KICK`, update callfds, register memory on `SET_MEM_TABLE`/`ADD_MEM_REG`, and restart sessions after memory replacement.

`vhost_register_unix_socket()` owns vhost-user socket registration: it unlinks stale socket files, rejects non-socket path collisions, registers the DPDK driver, sets enabled/disabled virtio features, registers callbacks, ORs protocol features, and starts the driver. Wrapper functions expose DPDK memory-table, unregister, and feature-query calls.

Device-level APIs manage coalescing, socket base path, device initialization/start/create, busy checks, unregister, vhost-user subsystem init/fini, and JSON session info. `vhost_user_fini()` starts a detached shutdown thread because DPDK socket removal can synchronously call SPDK callbacks and would otherwise deadlock.

Important invariants are lock ordering between global vhost lock and per-device session lock, not blocking SPDK callback threads during DPDK shutdown, preserving vring indices and packed phase bits across stop/restart, memory registration consistency, and backend start/stop completion through semaphores.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vhost/rte_vhost_user.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/vhost/vhost.c -->
# File Research: sources/virtualization/spdk/lib/vhost/vhost.c

This file implements common SPDK vhost controller and virtio-blk transport management.

Global state includes the allowed vhost core mask, a global vhost mutex, a list of created virtio-blk transports, a finalize callback, an RB tree of vhost devices keyed by name, and a registry of available virtio-blk transport operation tables.

`spdk_vhost_dev_next()` and `spdk_vhost_dev_find()` enumerate and look up devices in the RB tree. `vhost_parse_core_mask()` validates a requested cpumask is inside the SPDK environment core mask and nonempty, defaulting to the global mask when no mask string is supplied.

`vhost_dev_register()` validates name and cpumask, locks global vhost state, rejects duplicate names, stores the controller name, selects backend construction by backend type, and inserts the device into the RB tree. SCSI backends call `vhost_user_dev_create()`, while block backends call `virtio_blk_construct_ctrlr()`. `vhost_dev_unregister()` dispatches to the matching backend destroy/unregister path, removes the RB tree entry, frees the name, and invokes a pending fini callback when the last device is gone.

Accessors and operations expose device name, cpumask, backend info JSON, backend removal, and interrupt coalescing get/set. `spdk_vhost_lock()`, `spdk_vhost_trylock()`, and `spdk_vhost_unlock()` wrap the global mutex.

Initialization/finalization is split by backend. `spdk_vhost_scsi_init()` initializes vhost-user support and builds the core mask. `spdk_vhost_blk_init()` creates the default `vhost_user_blk` virtio-blk transport and builds the core mask. `spdk_vhost_scsi_fini()` starts vhost-user fini, then `vhost_fini()` removes remaining devices. `spdk_vhost_blk_fini()` destroys virtio-blk transports recursively.

Config JSON helpers emit controller replay RPCs and coalescing settings for SCSI and block devices. Block config also emits non-default virtio-blk transport creation RPCs, skipping the always-created `vhost_user_blk` transport.

Virtio-blk transport APIs register operation tables, create one instance per transport name, enumerate transports, dump transport options, find a target transport by name, and destroy transports through their ops.

Important invariants are global mutex protection around the device RB tree, backend-type dispatch consistency, no duplicate controller or transport names, and delayed finalize callback execution until devices/transports have been removed.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/vhost/vhost.c -->
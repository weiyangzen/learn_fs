# sources/distributed-fs/ceph-client/lib/vsprintf.c

## Purpose
Implements the kernel's core printf/snprintf/scnprintf/sprintf family, binary printf support, legacy simple string-to-number helpers, and `vsscanf`/`sscanf`. It also owns the extended kernel `%p` formatter namespace for symbols, resources, bitmaps, network addresses, UUIDs, times, device nodes, flags, dentries, files, block devices, clocks, escaped buffers, error pointers, and pointer disclosure policies.

## APIs and control flow
Exports include `simple_strtoull`, `simple_strtoul`, `simple_strntoul`, `simple_strtol`, `simple_strtoll`, `num_to_str`, `vsnprintf`, `vscnprintf`, `snprintf`, `scnprintf`, `vsprintf`, `sprintf`, optional `vbin_printf`/`bstr_printf`, `vsscanf`, and `sscanf`. `vsnprintf` repeatedly calls `format_decode`, copies literal spans, and dispatches numeric/string/pointer/width/precision/char states. `%p` enters `pointer`, which switches on alphanumeric suffixes and delegates to specialized helpers. `vsscanf` is a separate parser for whitespace, literals, suppression, widths, qualifiers, strings, constrained scansets, integers, `%n`, and `%%`.

## State, dependencies, and integration
Formatting is mostly per-call, but pointer output uses global state: `no_hash_pointers`, boot `hash_pointers` mode, `kptr_restrict`, a SipHash `ptr_key`, and `filled_random_ptr_key` synchronized by barriers. Dependencies span kallsyms, credentials, RCU, dcache/files, block, resources, networking, RTC/time, UUID, OF/fwnode, clocks, escaping, random/SipHash, unaligned access, and trace flag tables. This file is central to printk, procfs/sysfs text, diagnostics, tracing, and binary printk.

## Risks and test signals
Risks are address leaks, `%pK` context/credential mistakes, early RNG placeholders, varargs desynchronization after unsupported formats, and unsafe caller use of `sprintf`/`vsprintf`. Tests should cover printk format selftests, `%p` hashing and boot params, kallsyms variants, binary printf round trips, `sscanf` edge cases, truncation semantics, and config combinations for `CONFIG_BINARY_PRINTF`, `CONFIG_KALLSYMS`, `CONFIG_BLOCK`, `CONFIG_OF`, and clock support.

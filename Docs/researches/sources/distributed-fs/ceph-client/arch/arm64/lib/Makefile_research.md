# sources/distributed-fs/ceph-client/arch/arm64/lib/Makefile

Purpose: selects the ARM64 architecture library objects that provide low-level memory, string, checksum, delay, instruction encoding, MTE, KASAN tag, uaccess flushcache, and error-injection helpers.

Important APIs/types/functions: `lib-y` always includes clear/copy/user-copy/page-copy/checksum/instruction/string/tishift objects. Conditional object lines add `uaccess_flushcache.o`, `error-inject.o`, `mte.o`, and `kasan_sw_tags.o` based on kernel configuration.

Control flow: Kbuild consumes this Makefile during ARM64 library build and links these objects into the architecture library. Conditional symbols gate code that depends on persistent-memory cache flush support, function error injection, ARM64 MTE, and software-tag KASAN.

State and persistence: no runtime state. The file controls build-time object presence and therefore which exported symbols are available.

Dependencies/integration: integrates with top-level ARM64 Kbuild and configuration symbols `CONFIG_ARCH_HAS_UACCESS_FLUSHCACHE`, `CONFIG_FUNCTION_ERROR_INJECTION`, `CONFIG_ARM64_MTE`, and `CONFIG_KASAN_SW_TAGS`.

Risks: missing an object breaks exported symbol resolution for core kernel code; enabling an object without matching CPU/toolchain/config support can fail build or runtime alternatives. Order is conventional but objects must match source filenames.

Test signals: all relevant `allyesconfig`/`allnoconfig` ARM64 builds, symbol export checks for copy/string routines, and config matrix coverage for MTE, KASAN SW tags, and uaccess flushcache.

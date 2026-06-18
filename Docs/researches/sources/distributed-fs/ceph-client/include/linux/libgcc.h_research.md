# sources/distributed-fs/ceph-client/include/linux/libgcc.h

Purpose: declares compiler-runtime helper types and 64-bit arithmetic helper prototypes used by kernel libgcc-compatible routines.

Important APIs and types: `word_type` uses GCC's machine-word mode. `struct DWstruct` maps high/low words according to endianness, and `DWunion` overlays those words with a `long long`. Prototypes declare notrace helpers for doubleword shifts, signed/unsigned compare, and multiply: `__ashldi3`, `__ashrdi3`, `__cmpdi2`, `__lshrdi3`, `__muldi3`, and `__ucmpdi2`. Arch overrides can be included through `<asm/libgcc.h>`.

Control flow: compiler-generated calls or kernel arithmetic code resolve to these helpers on architectures needing software 64-bit operations.

State and persistence: stateless arithmetic interface only.

Dependencies and integration points: depends on architecture byte order and optional arch libgcc header; integrates compiler code generation with kernel-provided runtime helpers while avoiding tracing instrumentation.

Risks and test signals: risks include endian word ordering bugs, tracing recursion if `notrace` is lost, and arch override conflicts. Test arithmetic helper unit coverage, 32-bit builds, big/little-endian builds, and module link resolution.

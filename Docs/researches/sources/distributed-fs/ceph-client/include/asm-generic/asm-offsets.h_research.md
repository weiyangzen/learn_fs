# sources/distributed-fs/ceph-client/include/asm-generic/asm-offsets.h

Purpose: Forwards generic asm offset consumers to the generated `generated/asm-offsets.h` file.

Important APIs, types, and functions: Contains only `#include <generated/asm-offsets.h>`.

Control flow: Build-time include redirection only.

State and persistence: Generated offsets encode build-time structure layout constants for assembly code; this header stores none itself.

Dependencies and integration points: Depends on the kernel build having generated `asm-offsets.h`. Used by assembly and low-level code needing C structure offsets.

Risks and test signals: Risks are missing generated headers or stale offsets after structure changes. Test clean builds, incremental rebuilds touching offset-generating sources, and architecture assembly that includes the generic header.

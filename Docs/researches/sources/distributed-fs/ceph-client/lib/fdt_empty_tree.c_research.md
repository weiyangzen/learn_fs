# sources/distributed-fs/ceph-client/lib/fdt_empty_tree.c

## Purpose
Kernel wrapper for shared libfdt empty-tree creation. It includes the kernel libfdt environment and compiles `../scripts/dtc/libfdt/fdt_empty_tree.c`.

## Important APIs, Types, and Functions
The included implementation provides `fdt_create_empty_tree(void *buf, int bufsize)`. The wrapper has no independent API.

## Control Flow
`fdt_create_empty_tree()` creates a writable FDT in the supplied buffer, finishes the reserve map, opens and closes the root node, and finalizes the blob using libfdt sequential-write helpers.

## State and Persistence
State is entirely in the caller-provided buffer. No globals, allocation, or persistent kernel state are introduced by the wrapper.

## Dependencies and Integration Points
Depends on libfdt sequential-write functions from `fdt_sw.c` and `linux/libfdt_env.h`. It integrates with code that needs a minimal FDT blob as a starting point for later mutation.

## Risks
Failure handling depends on correct propagation of libfdt no-space or bad-state errors. Since the file is only a wrapper, shared libfdt changes alter behavior. Buffer size validation is critical.

## Test Signals
Create empty trees with too-small and sufficient buffers, validate resulting headers and root structure, and mutate the resulting tree with read-write libfdt APIs.

# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-heap.c

Purpose: implements the userspace DMA-BUF heap framework, creating `/dev/dma_heap/<heap>` character devices that allocate dma-buf file descriptors through heap-specific backends.

Important APIs/types/functions: exports `dma_heap_add()`, `dma_heap_get_drvdata()`, and `dma_heap_get_name()` in the `DMA_BUF_HEAP` namespace. Internal file operations include `dma_heap_open()` and `dma_heap_ioctl()` with `DMA_HEAP_IOCTL_ALLOC`. `struct dma_heap` stores heap name, ops, private data, char device, minor, and list node. Module parameter `mem_accounting` influences heap allocation GFP flags in heap backends.

Control flow: init allocates a char-device major range and creates class `dma_heap` with devnode path `dma_heap/<name>`. Heap registration validates name and allocate op, allocates a minor from an xarray, adds a cdev, creates the device node, enforces unique heap names under `heap_list_lock`, and links the heap into the global list. Opening a heap resolves the minor through the xarray and stores the heap in `file->private_data`. The ioctl path validates command number and structure sizes, copies userspace data into stack or heap scratch space, dispatches allocation, and copies results back. Allocation page-aligns length, rejects zero, calls the heap's `allocate()` op, and converts the returned dma-buf to an fd.

State and persistence behavior: registered heaps persist in the global list and xarray for the lifetime of the heap provider. Minors are limited to 128. Allocated buffers persist through dma-buf file references and are owned by heap-specific dma-buf ops.

Dependencies and integration points: depends on Linux cdev/class/device, xarray minor allocation, dma-buf fd export, uapi `linux/dma-heap.h`, and backend heap drivers such as `system_heap.c` and `cma_heap.c`.

Risks and test signals: duplicate heap names are detected after device creation, so error cleanup must destroy device/cdev/minor correctly. The ioctl compatibility logic is size-flexible but must zero unknown fields to keep ABI extension safe. Test signals include `/dev/dma_heap/system` and CMA node creation, allocation fd returned with valid flags, rejection of invalid heap/fd flags and zero size, unique name enforcement, and correct cleanup on registration failures.

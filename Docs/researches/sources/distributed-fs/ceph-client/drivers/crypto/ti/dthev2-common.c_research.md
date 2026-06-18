
# sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-common.c

Purpose: platform and common support for the TI DTHE V2 crypto accelerator. It owns device discovery, MMIO mapping, DMA channel setup, crypto engine lifecycle, global device list management, and delegates algorithm registration to the AES implementation.

Important APIs, types, and functions: `dthe_get_dev()` chooses a DTHE device for transform contexts and rotates the global list for basic load spreading. `dthe_copy_sg()` copies scatterlist entries by virtual address into a new scatterlist prefix. `dthe_dma_init()` requests and configures `"rx"`, `"tx1"`, and `"tx2"` DMA channels. `dthe_probe()` maps resources, links the device into the global list, starts a single-depth crypto engine, and calls `dthe_register_algs()`. `dthe_remove()` unregisters algorithms, exits the engine, releases DMA channels, and removes the device from the list.

Control flow: platform probe allocates `dthe_data`, maps MMIO resource 0, stores driver data, adds the device to `dthe_dev_list`, initializes DMA, allocates/starts `crypto_engine`, then registers algorithms. Error paths unwind in reverse order. Removal takes the device out of the global list first, unregisters algorithms, exits the engine, and releases all DMA channels.

State and persistence: software state is `struct dthe_data` plus the file-static `dthe_dev_list` protected by a spinlock. DMA channel pointers and the crypto engine persist for the platform device lifetime. There is no persistent storage beyond hardware registers and in-memory device list entries.

Dependencies and integration points: depends on platform driver probing, OF compatible `"ti,am62l-dthev2"`, devm allocation/ioremap, DMA engine slave configuration, crypto engine, and algorithm registration exported by `dthev2-aes.c`. The SHA TX DMA channel is requested even though this subset only registers AES algorithms, suggesting planned/shared support.

Risks and test signals: `dthe_get_dev()` assumes at least one device exists and uses `list_first_entry()` without an empty-list guard, so algorithm use before probe or after teardown would be dangerous if registration ordering breaks. `dthe_copy_sg()` uses `sg_virt()` and therefore assumes CPU-addressable scatterlist entries. Probe failure unwind and remove paths should be tested with missing DMA channels, engine start failure, algorithm registration failure, and multiple DTHE devices to verify list rotation and locking.

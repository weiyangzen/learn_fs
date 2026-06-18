<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/paging.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/paging.c

Purpose: allocates, fills, maps, commands, and frees firmware paging blocks for older non-gen2 devices.

Important APIs/functions: exported `iwl_init_paging()` and `iwl_free_fw_paging()` are the public lifecycle. Private helpers allocate DMA-backed pages, find the paging separator in the firmware image, copy CSS and paging data, DMA-sync blocks, and send `FW_PAGING_BLOCK_CMD`.

Control flow: `iwl_init_paging()` exits for gen2 or non-paged images. Otherwise it allocates one 4 KiB CSS block plus 32 KiB paging blocks, copies the CSS section and paged image data after `PAGING_SEPARATOR_SECTION`, validates last-block sizing, sends physical page addresses shifted by page size, and frees everything on errors.

State and persistence: stores blocks in `fwrt->fw_paging_db[]`, plus `num_of_paging_blk` and `num_of_pages_in_last_blk`. Memory remains DMA-mapped until `iwl_free_fw_paging()`.

Dependencies/integration: consumes paging constants and image sections from `img.h`, sends firmware command definitions from `fw/api/commands.h`, and integrates with dump code that can capture paging blocks.

Risks/test signals: off-by-one block accounting and DMA mapping size/order are critical. Test no-paging images, missing separator/CSS/data, exact and partial last blocks, allocation and DMA mapping failures, command send failures with cleanup, and dump capture of paged blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/paging.c -->

# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/boot.c

Purpose: host-side MHI boot and firmware image transfer support. It allocates BHI/BHIE DMA buffers, loads firmware through BHI or BHIE vector interfaces, handles firmware boot continuation, prepares/downloads RDDM crash dumps, and transitions the controller toward READY/mission mode.

Important APIs: `mhi_rddm_prepare()`, `mhi_download_rddm_image()`, `mhi_alloc_bhie_table()`, `mhi_free_bhie_table()`, `mhi_fw_load_handler()`, and `mhi_download_amss_image()`. Internal helpers allocate BHI buffers, copy firmware into segmented BHIE vectors, choose BHI/BHIE/FBC load mode, and dump BHI error registers.

Control flow: firmware handler reads hardware serial number, skips loading if current EE is already pass-through, selects EDL or normal firmware, accepts pre-supplied firmware data for FBC, requests firmware if needed, transfers SBL over BHI/BHIE, resets device state, optionally prepares full firmware BHIE vectors for FBC, releases firmware, and calls `mhi_ready_state_transition()`. AMSS download later rings BHIE TX vector DB using the prepared table.

RDDM behavior: preparation fills vector table entries and programs RXVEC registers. Normal RDDM waits on `state_event`; panic path avoids locks where unsafe, forces SYS_ERR/reset if needed, and polls registers with udelay.

State and persistence: stores DMA-coherent image buffers in `struct image_info`, controller serial number, `fbc_image`, PM state, device state, and waitqueue-observed BHIE/BHI status. Buffers are freed on errors or later cleanup.

Dependencies and integration: depends on firmware loader, DMA coherent allocation, MHI register helpers, PM locks/states, wait queues, random nonzero sequence IDs, BHI/BHIE register definitions, and controller callbacks such as `mhi_soc_reset()`.

Risks: firmware size/segment metadata must be consistent; FBC combined ELF handling assumes a second ELF header after `sbl_size`; panic RDDM deliberately bypasses normal locking; timeout/status handling drives PM error states. Test signals include BHI and BHIE boot, FBC staged boot, EDL image path, missing firmware errors, BHI error dump, AMSS transfer, RDDM normal and panic download, timeout, PM error wakeups, and DMA cleanup.

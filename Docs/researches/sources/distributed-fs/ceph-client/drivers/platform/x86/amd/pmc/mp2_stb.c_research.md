# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/mp2_stb.c

Purpose: `mp2_stb.c` adds MP2 previous-boot STB dumping to the AMD PMC debugfs tree. It discovers a PCI MP2 STB device, maps its MMIO BAR, allocates DMA/coherent buffers, issues MP2 mailbox commands, and exposes captured STB data through `stb_read_previous_boot`.

Important APIs, types, and functions: `struct mp2_cmd_base`, `struct mp2_cmd_response`, and `struct mp2_stb_data_valid` model MP2 command/status registers. `amd_mp2_stb_init()` probes PCI device `PCI_DEVICE_ID_AMD_MP2_STB`, enables the device, maps BAR 2, sets DMA mask, and registers debugfs. `amd_mp2_process_cmd()` validates data availability/length, allocates buffers via `amd_mp2_stb_region()`, sends a DMA command, waits for response, and copies data. `amd_mp2_stb_deinit()` clears bus mastering, releases PCI reference and devres group, and clears `dev->mp2`.

Control flow: PMC probe calls `amd_mp2_stb_init()` when compiled. The debugfs open path lazily fetches STB data on first open; later opens reuse cached `mp2->stbdata` while `is_stb_data` is true. Reads stream the cached buffer. Deinit runs during PMC removal.

State and persistence: `struct amd_mp2_dev` is devm-allocated under the PMC device but owns resources under the MP2 PCI device through a devres group. It stores MMIO mapping, coherent DMA address, copied data buffer, length, and cache-valid flag. Previous-boot STB content is fetched from MP2 firmware/device state and cached until deinit.

Dependencies and integration points: depends on PCI, DMA coherent allocation, MMIO polling, debugfs, and the PMC device debugfs root. It uses `writeq()` to pass DMA address and MP2 C2P/P2C registers for command exchange.

Risks: `amd_mp2_stb_region()` checks `!mp2->stbdata` before allocation, but `stb_len` can change if firmware reports a different length on a later uncached attempt. Cached data is never refreshed after first success. Error cleanup spans two devices and relies on devres group release. Debugfs open can fail with `-EBADMSG`, `-EMSGSIZE`, timeout, or unsupported status depending on firmware registers.

Test signals: PCI device discovery, BAR2 mapping, DMA mask success, debugfs file creation, valid data marker `0xA`, supported length codes 1 and 4 mapping to 2 KiB/16 KiB, MP2 response status 2, stable cached reads, and deinit releasing PCI resources.

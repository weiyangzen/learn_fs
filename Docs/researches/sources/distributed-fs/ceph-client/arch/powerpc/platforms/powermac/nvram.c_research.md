# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/nvram.c

Purpose: implements PowerMac NVRAM access for direct-mapped, indirect-addressed, PMU-backed, and Core99 flash-backed NVRAM. It wires the platform `ppc_md.nvram_*` callbacks, discovers CHRP partition offsets, and provides exported XPRAM helpers.

Important APIs/types/functions: structures include `chrp_header` and `core99_header`. Public functions are `pmac_nvram_init`, `pmac_get_partition`, `pmac_xpram_read`, and `pmac_xpram_write`. Core99 support uses `core99_nvram_read_byte`, `core99_nvram_write_byte`, `core99_nvram_read`, `core99_nvram_write`, `core99_nvram_size`, `core99_calc_adler`, `core99_check`, `core99_nvram_setup`, and `core99_nvram_sync`. Flash writers are `sm_erase_bank`, `sm_write_bank`, `amd_erase_bank`, and `amd_write_bank`.

Control flow: init locates the `nvram` OF node and its resources. Core99 flash maps two 8 KiB banks, validates signatures/checksums/Adler values, selects the bank with the highest generation, copies it into `nvram_image`, and installs buffered read/write/sync callbacks. Non-Core99 32-bit paths choose direct MMIO, indirect address/data MMIO, or PMU request based on resource count and system controller. `lookup_partitions` scans CHRP headers on NewWorld machines or uses fixed OldWorld offsets. `core99_nvram_sync` compares the shadow image to the active bank, updates generation/checksum/adler, flips banks, erases, and writes the inactive bank.

State and persistence: Core99 writes are staged in `nvram_image` and become persistent only when `nvram_sync` or `machine_shutdown` calls `core99_nvram_sync`. Direct, indirect, and PMU paths write through immediately. Global state tracks mapping count, current Core99 bank, partition offsets, flash operation callbacks, and a raw spinlock for serialized NVRAM access.

Dependencies/integration: depends on OF address parsing, memblock allocation, low-level MMIO, PMU ADB requests, `ppc_md` machine callbacks, CHRP NVRAM conventions, and exported `pmac_nvram_*` users such as time, boot settings, and XPRAM clients.

Risks: Core99 flash erase/write loops poll up to fixed software timeouts and then verify whole-bank contents. The erase/write helpers calculate `base` using `core99_bank` instead of their `bank` argument, which makes correctness depend on `core99_bank` being switched before the helper call. Debug mode adds a 2 second delay after sync. Partition scanning trusts header lengths enough to advance offsets. PMU byte access may poll when the system is not fully running.

Test signals: validate direct, indirect, PMU, and Core99 initialization; corrupt Core99 signature/checksum/adler cases; generation-bank selection; write shadow bytes then sync and verify bank flip; flash timeout and verify-failure paths; CHRP partition scanning for `common` and `APL,MacOS75`; XPRAM boundary checks and negative partition offsets.

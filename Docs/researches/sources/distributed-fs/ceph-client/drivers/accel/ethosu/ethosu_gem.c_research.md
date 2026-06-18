# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_gem.c

Purpose: implements Ethos-U GEM BO allocation and command-stream BO validation. It uses DMA GEM objects for data buffers and stores parsed command-stream region-size/output metadata on command BOs.

Important APIs/functions: `ethosu_gem_create_object()` provides DRM object allocation; `ethosu_gem_create_with_handle()` allocates a DMA GEM BO, records flags, creates a handle, and returns actual size. `ethosu_gem_mmap()` rejects mmap for BOs with `DRM_ETHOSU_BO_NO_MMAP`. `ethosu_gem_cmdstream_create()` allocates a DMA BO, copies user command words, validates them, stores `ethosu_validated_cmdstream_info`, and publishes a handle. Validation tracks command state, decodes immediate/address commands, computes maximum region sizes for DMA, IFM/IFM2/OFM, weights, and scales, and marks output regions.

Control flow: command-stream create ioctl calls this file before submit. Submit later compares required region sizes against supplied BO sizes and uses output-region flags for reservation fences.

State and persistence: each `ethosu_gem_object` stores flags and optional command metadata until BO free. Command BO data is copied into DMA memory.

Dependencies: DRM DMA GEM helpers, Ethos-U register/opcode definitions, UAPI flags.

Risks: command validation is a software parser for hardware command streams; unsupported U85 resize currently only warns/TODO. Address/stride arithmetic and U65/U85 opcode overlaps are subtle. Missing validation can permit out-of-BO device access.

Test signals: validated Vela command streams, malformed missing setup, oversized region access, NO_MMAP enforcement, U65/U85 elementwise differences, DMA stride modes, and command BO used incorrectly as region BO.

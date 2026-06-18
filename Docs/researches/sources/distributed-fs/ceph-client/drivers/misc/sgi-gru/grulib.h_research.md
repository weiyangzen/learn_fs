# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grulib.h

Purpose: defines the user/kernel ABI for `/dev/gru`, including ioctl numbers, request structures, GSEG address helpers, dump formats, and temporary test/config interfaces. It is the public UAPI-style header for GRU user context management.

Important APIs/types: ioctl IDs include `GRU_CREATE_CONTEXT`, `GRU_SET_CONTEXT_OPTION`, `GRU_USER_GET_EXCEPTION_DETAIL`, `GRU_USER_CALL_OS`, `GRU_USER_UNLOAD_CONTEXT`, `GRU_DUMP_CHIPLET_STATE`, `GRU_GET_GSEG_STATISTICS`, `GRU_USER_FLUSH_TLB`, `GRU_GET_CONFIG_INFO`, and `GRU_KTEST`. Request structures include `gru_create_context_req`, `gru_unload_context_req`, `gru_set_context_option_req`, `gru_flush_tlb_req`, `gru_dump_chiplet_state_req`, `gru_dump_context_header`, `gru_get_gseg_statistics_req`, and `gru_config_info`.

Control flow: users create a GRU context, mmap one or more GSEGs, set placement/options, handle TLB or exception events via ioctl calls, optionally unload or flush, and fetch statistics/dumps for diagnostics. Macros such as `CONTEXT_WINDOW_BYTES()`, `THREAD_POINTER()`, and `GSEG_START()` map between a multi-thread context window and per-thread GSEG addresses.

State and persistence: this header defines ABI data copied between user space and the driver. Persistent kernel state lives in `gru_thread_state`, `gru_vma_data`, and GRU hardware contexts; user-visible request structures identify the GSEG base, selected options, address ranges, dump targets, and output buffers.

Dependencies and integration: depends on GRU constants and `struct gru_gseg_statistics` from lower GRU headers. It is consumed by ioctl handling outside this item and by `grutables.h` declarations that share request structures across driver modules.

Risks: ioctl numbers and structure layouts are ABI, so changes can break user programs. Several comments mark interfaces as primarily for tests or temporary emulator/debug use. Pointer fields in dump requests require careful copy_from_user/copy_to_user validation in ioctl handlers.

Test signals: `GRU_KTEST`, `GRU_GET_CONFIG_INFO`, dumps, statistics, and flush ioctls are explicit validation hooks. Runtime failures should be correlated with exception-detail and gseg-statistics queries.

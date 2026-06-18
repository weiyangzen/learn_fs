# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pmc.h

## Purpose
`pmc.h` declares the PMC debug/capture interface shared between `pmc.c` and debugfs. It also defines the marker used to initialize unused PMC capture dwords.

## Important APIs, Types, And Functions
The header defines `PCM_DATA_INVALID_DW_VAL` and prototypes for `wil_pmc_init()`, `wil_pmc_alloc()`, `wil_pmc_free()`, `wil_pmc_last_cmd_status()`, `wil_pmc_read()`, `wil_pmc_llseek()`, and `wil_pmcring_read()`.

## Control Flow
There is no executable flow. Debugfs calls these declarations to allocate/free PMC memory, read capture data, seek within it, and dump the descriptor ring.

## State And Persistence
State is owned by `struct pmc_ctx` inside `wil6210_priv`, not by the header. The invalid dword marker is persisted into allocated coherent descriptor buffers during initialization.

## Dependencies And Integration Points
The prototypes depend on `struct wil6210_priv`, Linux `struct file`, `seq_file`, user pointers, and loff_t types. `debugfs.c` includes this header to expose PMC files.

## Risks
The header lacks an include guard in this snapshot; repeated inclusion is currently benign because it only has a macro and prototypes, but adding definitions would need a guard. Prototype users must include suitable forward declarations or headers before this file.

## Test Signals
Build coverage is the main signal: debugfs and PMC translation units should compile with this header. Runtime PMC tests are covered under `pmc.c`.

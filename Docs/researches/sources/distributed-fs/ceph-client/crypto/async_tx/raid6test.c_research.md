<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/raid6test.c -->
# sources/distributed-fs/ceph-client/crypto/async_tx/raid6test.c

## Purpose

`raid6test.c` is a kernel self-test module for asynchronous RAID-6 recovery. It allocates pages, generates random data and syndromes, simulates all two-disk failure combinations for selected disk counts, invokes async recovery helpers, and validates recovered data and syndrome consistency.

## Important APIs, Types, and Flow

Global arrays `data`, `dataptrs`, `dataoffs`, and `addr_conv` hold test pages and async address conversion scratch. `raid6_dual_recov()` selects the recovery path by failed disk class: P+Q rebuilds syndrome, data+Q reconstructs data with `async_xor()` then rebuilds syndrome, data+P calls `async_raid6_datap_recov()`, and data+data calls `async_raid6_2data_recov()`. It then chains `async_syndrome_val()` with a completion callback and checks `sum_check_flags`.

`test()` creates baseline random data, overwrites P and Q pages, calls `async_gen_syndrome()`, then loops over failure pairs through `test_disks()`. `raid6_test()` allocates `NDISKS + 3` pages and runs special cases for 4, 5, 11, 12, 24, and 64 disks before freeing pages.

## State, Dependencies, and Integration

State is module-global test memory and temporary replacement pages `recovi`, `recovj`, and `spare`. The file depends on async_tx RAID6 APIs, random bytes, page allocation, completions, and late init ordering so built-in DMA providers can register first.

## Risks and Test Signals

The test itself is a signal: timeout logs point to async completion/pending issues, validation failures point to syndrome or recovery bugs, and `memcmp()` failures identify wrong recovered disks. Risks include PAGE_SIZE-only coverage, fixed maximum disk count, reliance on low-level pages being virtually addressable, and returning `0` even when test failures are logged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/raid6test.c -->

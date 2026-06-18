# sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead.h

## Purpose
`hdd_readahead.h` declares the read-ahead/read-behind configuration class for chunkserver HDD reads.

## Important APIs, Types, And Functions
- `HDDReadAhead::maxBlocksToBeReadBehind` and `blocksToBeReadAhead` return current atomic block counts.
- `setMaxReadBehind_kB` and `setReadAhead_kB` convert kilobytes to MFS block counts and store them.
- `kBToBlocks` computes `(kB * 1024) / MFSBLOCKSIZE`.
- `extern HDDReadAhead gHDDReadAhead` declares the process-global instance.

## Control Flow
Configuration code sets values in KiB. Read paths fetch block counts and pass them into HDD I/O functions to decide prefetch/read-behind windows.

## State And Persistence
State is two `std::atomic<uint16_t>` fields. The class does not persist settings itself.

## Dependencies And Integration Points
It depends on `MFSBLOCKSIZE` from `protocol/MFSCommunication.h` and is consumed by HDD read code and tests.

## Risks
- `kBToBlocks` multiplies `uint32_t kB` by 1024 before dividing, so extremely large inputs can overflow before truncation to `uint16_t`.
- Atomic fields lack explicit default initializers in the class definition.
- Conversion truncates partial blocks by design; callers must understand that sub-block KiB values become zero.

## Test Signals
`hdd_readahead_unittest.cc` covers conversion boundaries around one and two block sizes and a larger value.

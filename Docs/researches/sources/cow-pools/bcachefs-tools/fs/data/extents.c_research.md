# File Research: sources/cow-pools/bcachefs-tools/fs/data/extents.c

Large extent utility implementation covering read pointer selection, btree pointer validation, extent merging, CRC entry packing, durability, pointer mutation, cached pointer cleanup, formatting, validation, byte-swapping, and key cutting.

Key responsibilities:
- Tracks and formats per-device read failures, including checksum, IO, and EC reconstruction errors.
- Chooses read devices with `bch2_bkey_pick_read_device()`:
  - Ignores stale cached pointers.
  - Honors hard/soft preferred-device flags.
  - Handles missing/offline devices.
  - Selects EC reconstruction when needed.
  - Biases random choice by squared device latency.
  - Returns precise no-device/checksum/io error classes.
- Validates and formats `KEY_TYPE_btree_ptr` and `KEY_TYPE_btree_ptr_v2`, including min-key/version compatibility.
- Merges adjacent extents when pointer order, devices, generations, EC stripe pointers, compression, CRC nonce/type, bucket boundary, and checksum mergeability permit it.
- Validates and merges reservation keys.
- Packs/unpacks and appends CRC entries in crc32/crc64/crc128 forms based on checksum size, extent size, and nonce range.
- Narrows CRC entries when rewriting another replica so remaining replicas point only to live data.
- Computes pointer counts, dirty pointer counts, allocated/fully allocated pointer counts, compressed sectors, incompressible status, replica count, and durability.
- Drops extent entries, pointers, devices, and EC stripe entries with helpers that preserve associated CRC/stripe metadata rules.
- Appends decoded pointers and optional stripe pointers to keys, reusing or appending matching CRC entries.
- Tests for devices/targets/bad devices and pointer/extent equivalence.
- Manages cached pointers:
  - Drops duplicate cached pointers.
  - Rejects cached pointers on EC data.
  - Drops stale/bad/evacuating/wrong-target cached pointers.
  - Converts excess durability to cached pointers or removes pointers entirely.
- Drops extra EC durability while preserving requested replica durability.
- Formats extent pointers, CRCs, and all extent entry types.
- Validates extent pointer entries:
  - Unknown entry types.
  - Btree pointer allowed entry types.
  - duplicate devices.
  - pointer bounds and bucket spanning.
  - checksum and compression type validity.
  - encoded extent size.
  - encrypted nonce consistency.
  - redundant CRC/stripe entries.
  - written/unwritten mixing.
  - missing/all-invalid dirty pointers.
- Swaps extent pointer entries for endian conversion.
- Adds extent flags entry, requesting the incompatible feature first.
- Cuts front/back of keys for extents, reflinks, inline data, and indirect inline data while adjusting sizes, pointer offsets, CRC offsets, reflink indices, and value size.

Important interactions:
- Central dependency for read path, write path, btree validation, EC creation, compression, checksum, reconcile, and device removal.
- Uses checksum mergeability from `checksum.h` and compression metadata from `compress.h`.
- EC pointer semantics interact with `ec/trigger.h` pointer matching and stripe pointer validation.
- Durability helpers account for EC redundancy as pointer durability.

Notable concerns:
- Cached pointers are deliberately incompatible with EC and are dropped.
- Extents may not straddle buckets; merge and validation enforce bucket-boundary constraints.
- Validation distinguishes btree pointers from data extents because dead btree nodes may keep pointer fields without becoming `KEY_TYPE_error`.
- Read selection can force EC reconstruction via static branch for testing/debug behavior.

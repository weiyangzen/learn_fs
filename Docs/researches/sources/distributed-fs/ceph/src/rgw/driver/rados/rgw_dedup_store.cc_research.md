# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_store.cc

## Purpose
`rgw_dedup_store.cc` implements the disk record and slab storage layer for RGW dedup. It serializes bucket-index-derived object records into fixed-size blocks, writes blocks as slab objects, reads records back by block and record id, and provides helpers for per-MD5-shard output streams.

## Important APIs, Types, And Functions
`disk_record_t` constructors build records either from a SAL bucket plus object metadata or from serialized bytes. `serialize()`, `length()`, and `validate()` define the on-disk record format. Records include MD5, BLAKE3 hash fields, object size, part count, bucket identity, tenant, instance, storage class, ref tag, and serialized manifest.

`disk_block_t::init()`, `add_record()`, and `close_block()` manage one 8 KiB block. `disk_block_header_t::deserialize()` and `verify()` validate loaded block headers, magic markers, record counts, and block id.

`disk_block_id_t::get_slab_name()` maps a block id and MD5 shard to a slab object name in the format `SLB.%03X.%02X.%04X`. `load_record()`, `load_slab()`, and `store_slab()` are the RADOS read/write primitives. `disk_block_seq_t` appends records to a sequence of blocks and flushes slabs. `disk_block_array_t` owns one sequence per MD5 shard for a work shard.

## Control Flow
Ingress creates `disk_record_t` instances from bucket-index entries. A `disk_block_array_t` chooses a `disk_block_seq_t` by `md5_low % num_md5_shards`. `add_record()` validates the record, tries the current block, closes and advances when full, flushes the slab when the block array is exhausted, and returns a block id plus record id for dedup table references.

At phase end, `flush_output_buffers()` writes a final block for every MD5 shard. Even empty sequences write a terminating block so the MD5 stage can distinguish no work from missing work.

The read path derives the slab object name and byte offset from `disk_block_id_t`, reads one block, deserializes the header, verifies expected block id and record count, constructs a `disk_record_t`, validates it, and compares the key fields against the target record before returning the source record.

## State And Persistence Behavior
Slab objects are RADOS objects named by MD5 shard, worker shard, and slab id. Each slab contains up to 256 fixed 8 KiB blocks. Each block contains a packed header and up to 32 variable-length records. Header offset is reused as a magic value when closed: `BLOCK_MAGIC` indicates more blocks follow, and `LAST_BLOCK_MAGIC` marks termination.

Records are serialized in little-endian Ceph order for numeric fields, while strings and manifest bufferlists are concatenated after the packed header. Fastlane records omit ref tag and manifest payload and assert those lengths are zero.

## Dependencies And Integration Points
The store layer uses librados `IoCtx`, RGW object manifests, SAL bucket identity, `parsed_etag_t`, BLAKE3 constants, dedup stats, and Ceph bufferlist helpers. It feeds `rgw_dedup_table.*` and the main background pipeline.

## Risks And Edge Cases
The serialized constructor uses lengths from the on-disk packed header while advancing with some raw packed lengths; malformed records could stress length validation. `load_record()` requires an exact `DISK_BLOCK_SIZE` read and treats short reads as errors. Header validation does not include CRC, and comments note a future CRC. `disk_block_array_t` aborts the process if raw memory is too small for the requested MD5 shard count.

## Test Signals
Tests should cover record serialize/deserialize round trips, endian conversion, fastlane omission, max record size, block full behavior, last-block marker handling, slab object name formatting, empty terminating slab writes, fragmented bufferlist reads, and corrupt header or wrong block id failures.

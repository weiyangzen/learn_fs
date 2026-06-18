# sources/distributed-fs/ceph-client/drivers/nvdimm/label.c

## Purpose
`label.c` implements NVDIMM and CXL namespace label parsing, validation, allocation, garbage collection, claim-class encoding, and persistent label updates. It owns the copy-on-write namespace-index protocol used to safely update DIMM label storage and the logic that maps active labels to DPA resource reservations.

## Important APIs, Types, And Functions
Public functions include `sizeof_namespace_label()`, `nvdimm_num_label_slots()`, `sizeof_namespace_index()`, `nd_label_reserve_dpa()`, `nd_label_data_init()`, `nd_label_active_count()`, `nd_label_active()`, `nd_label_alloc_slot()`, `nd_label_free_slot()`, `nd_label_nfree()`, `nsl_validate_type_guid()`, `nsl_get_claim_class()`, `nd_pmem_namespace_label_update()`, and `nd_label_init()`.

Validation helpers include `best_seq()`, `__nd_label_validate()`, `nd_label_validate()`, `nsl_validate_checksum()`, `slot_valid()`, and label access helpers from `nd.h`. Update helpers include `nd_label_write_index()`, `__pmem_label_update()`, `init_labels()`, `del_labels()`, and claim-class GUID/UUID conversion functions.

## Control Flow
`nd_label_data_init()` reads the DIMM config-data area. It first computes the maximum possible index size using 128-byte labels, allocates the full config-data buffer, reads enough bytes to validate both namespace indexes, probes label size by trying 128 and 256 bytes, identifies the current index, copies it to the next index staging area, then reads only active labels based on the free bitmap.

Validation checks namespace-index signature, version-implied label size, checksum, nonzero sequence, offsets, index size, and label-slot bounds. If both indexes are valid, `best_seq()` chooses the active one using the two-bit sequence progression. Active label iteration walks clear bits in the free bitmap and verifies slot number plus checksum.

Label updates are copy-on-write. `nd_pmem_namespace_label_update()` first writes labels with `NSLABEL_FLAG_UPDATING` for all mappings, then rewrites them without the flag after all mappings succeed. `__pmem_label_update()` allocates a free slot from the next index, fills a new label with UUID/name/flags/position/cookie/DPA/size/LBA/claim class/checksum, writes the label, reaps old labels for the same UUID or marked victims, then writes the next namespace index with an incremented sequence. Only after index write success does it update in-memory label tracking.

Delete frees slots for matching UUIDs, may clear label tracking when no active labels remain, and writes a new index. Initial label-area creation writes both namespace indexes with initialized free bitmaps and sequences.

## State And Persistence Behavior
Persistent state lives in two namespace indexes and an array of labels in DIMM config-data storage. Indexes are never updated in place as current; the alternate index is staged and written with a new sequence, then current/next pointers swap in memory. Labels are also written into free slots before the index that references them becomes active. This protects against partial writes and lets startup recover by choosing the best valid index.

The code supports EFI labels and CXL labels. EFI labels use GUIDs and interleave-set cookies; CXL labels use UUIDs for equivalent type and abstraction fields and treat some EFI concepts as always valid. DPA reservations mirror active labels in volatile resource trees using IDs like `pmem-<uuid>`.

## Dependencies And Integration Points
The file depends on DIMM config-data command wrappers in `dimm_devs.c`, checksum helper `nd_fletcher64()` from `core.c`, DPA resource allocation in `dimm_devs.c`, namespace update requests from `namespace_devs.c`, and interleave-set cookies/type GUIDs from region code. It initializes known BTT/PFN/DAX/CXL GUIDs and UUIDs at libnvdimm startup.

## Risks And Edge Cases
Label-size auto-detection must avoid trusting unvalidated media. Sequence comparison uses only two bits, so invalid equal or zero sequences are rejected. The update protocol can leave `UPDATING` labels if interrupted between first and second passes; readers and tooling must understand that flag. Slot allocation requires the bus lock; missing locking can race with namespace provisioning. The code preserves unknown claim classes by not overwriting existing abstraction identifiers when claim class is unknown.

## Test Signals
Tests should cover empty/invalid label areas, valid single and dual indexes, sequence wrap behavior, 128-byte and 256-byte EFI labels, CXL label fields, checksum failures, free bitmap slot allocation/free, active label counting, DPA reservation from labels, namespace grow/shrink/delete label updates, interrupted update with `UPDATING`, claim-class GUID/UUID mapping, and label-area initialization from scratch.

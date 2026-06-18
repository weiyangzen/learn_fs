# sources/distributed-fs/lizardfs/src/protocol/cstoma_unittest.cc

Purpose: Exercises selected chunkserver-to-master packet helpers from `cstoma.h`, including the special in-place status overwrite helper.

Important APIs/types/functions: Test cases `OverwriteStatusField`, `RegisterHost`, `RegisterChunks`, `RegisterSpace`, `SetVersion`, `DeleteChunk`, `Replicate`, and `Status`; `cstoma::overwriteStatusField`; chunk type constants; `LIZARDFS_VERIFY_INOUT_PAIR`.

Control flow: Tests serialize a packet, validate its type header, strip the header, and deserialize the payload into output variables. The overwrite test mutates a serialized `setVersion` status byte before deserialization to prove the hard-coded status offset is correct for that layout.

State and persistence: Uses only local vectors and scalar test variables. It models wire state but does not touch network sockets or persistent metadata.

Dependencies and integration: Depends on GTest, `common/mfserr.h` for status codes, chunk constants, and generic packet test utilities. It validates contracts used by chunkservers reporting to masters.

Risks and test signals: Strong signal for selected packet field order and EC chunk type round trips. Coverage is not exhaustive for all packet families in `cstoma.h`, and negative validation of wrong versions/short payloads is absent.
